from flask import Flask, render_template, request, jsonify, Response
from typing import Union, Tuple
import json
import subprocess
import requests
import os

app = Flask(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/opt/stacks/nanobot/config/config.json")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
DOCKER_PROXY_URL = os.environ.get("DOCKER_PROXY_URL", "http://docker-socket-proxy:2375")


def read_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def write_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_ollama_models():
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.ok:
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception as e:
        print(f"Ollama error: {e}")
    return []


@app.route("/")
def index():
    config = read_config()
    defaults = config.get("agents", {}).get("defaults", {})
    return render_template(
        "index.html",
        current_model=defaults.get("model", ""),
        current_provider=defaults.get("provider", ""),
        ollama_models=get_ollama_models(),
    )


@app.route("/api/models")
def api_models():
    return jsonify(get_ollama_models())


@app.route("/api/config")
def api_config():
    config = read_config()
    defaults = config.get("agents", {}).get("defaults", {})
    return jsonify(
        {"model": defaults.get("model", ""), "provider": defaults.get("provider", "")}
    )


@app.route("/api/update", methods=["POST"])
def api_update():
    """Update default agent configuration (model, provider)."""
    data = request.json
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()
    if not model or not provider:
        return jsonify({"success": False, "error": "Champs requis"}), 400
    try:
        config = read_config()
        config.setdefault("agents", {}).setdefault("defaults", {})
        config["agents"]["defaults"]["model"] = model
        config["agents"]["defaults"]["provider"] = provider
        write_config(config)
        return jsonify(
            {
                "success": True,
                "message": f"✅ Config mise à jour : {provider} / {model}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/coder")
def api_coder():
    """Retrieve Coder configuration (model, provider, maxTokens)."""
    try:
        config = read_config()
        coder = config.get("agents", {}).get("coder", {})
        return jsonify(
            {
                "model": coder.get("model", ""),
                "provider": coder.get("provider", ""),
                "maxTokens": coder.get("maxTokens", 16384),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/coder/update", methods=["POST"])
def api_coder_update():
    """Update Coder configuration (model, provider, maxTokens)."""
    data = request.json
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()
    max_tokens = data.get("maxTokens")

    if not model or not provider:
        return jsonify({"success": False, "error": "Modèle et provider requis"}), 400

    try:
        max_tokens = int(max_tokens)
        if max_tokens <= 0:
            return jsonify({"success": False, "error": "maxTokens doit être > 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "maxTokens invalide"}), 400

    try:
        config = read_config()
        config.setdefault("agents", {})
        config["agents"]["coder"] = {
            "model": model,
            "provider": provider,
            "maxTokens": max_tokens,
        }
        write_config(config)
        return jsonify(
            {
                "success": True,
                "message": f"✅ Coder configuré : {provider} / {model} ({max_tokens} tokens)",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/vision")
def api_vision():
    """Retrieve Vision configuration (model, provider, optional maxTokens)."""
    try:
        config = read_config()
        vision = config.get("agents", {}).get("vision", {})
        return jsonify(
            {
                "model": vision.get("model", ""),
                "provider": vision.get("provider", ""),
                "maxTokens": vision.get("maxTokens"),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/vision/update", methods=["POST"])
def api_vision_update():
    """Update Vision configuration (model, provider, optional maxTokens)."""
    data = request.json
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()
    max_tokens = data.get("maxTokens")

    if not model or not provider:
        return jsonify({"success": False, "error": "Modèle et provider requis"}), 400

    # maxTokens is optional for Vision
    if max_tokens:
        try:
            max_tokens = int(max_tokens)
            if max_tokens <= 0:
                return jsonify(
                    {"success": False, "error": "maxTokens doit être > 0"}
                ), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "maxTokens invalide"}), 400

    try:
        config = read_config()
        config.setdefault("agents", {})
        config["agents"]["vision"] = {"model": model, "provider": provider}
        if max_tokens:
            config["agents"]["vision"]["maxTokens"] = max_tokens

        write_config(config)
        tokens_info = f" ({max_tokens} tokens)" if max_tokens else ""
        return jsonify(
            {
                "success": True,
                "message": f"✅ Vision configurée : {provider} / {model}{tokens_info}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/restart", methods=["POST"])
def api_restart():
    try:
        # 1. Obtenir l'ID du container nanobot-gateway
        resp = requests.get(f"{DOCKER_PROXY_URL}/containers/json?all=1", timeout=5)
        resp.raise_for_status()
        containers = resp.json()
        container_id = None
        for c in containers:
            if any("nanobot-gateway" in name for name in c.get("Names", [])):
                container_id = c["Id"]
                break
        if not container_id:
            return jsonify(
                {"success": False, "error": "Container nanobot-gateway introuvable"}
            ), 404

        # 2. Restart via l'API
        r = requests.post(
            f"{DOCKER_PROXY_URL}/containers/{container_id}/restart", timeout=30
        )
        if r.status_code in (204, 200):
            return jsonify(
                {
                    "success": True,
                    "message": "🔄 Container nanobot-gateway restarté avec succès",
                }
            )
        return jsonify(
            {"success": False, "error": f"HTTP {r.status_code}: {r.text}"}
        ), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8899, debug=False)
