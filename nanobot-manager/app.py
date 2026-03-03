from flask import Flask, render_template, request, jsonify
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
    return render_template("index.html",
        current_model=defaults.get("model", ""),
        current_provider=defaults.get("provider", ""),
        ollama_models=get_ollama_models()
    )

@app.route("/api/models")
def api_models():
    return jsonify(get_ollama_models())

@app.route("/api/config")
def api_config():
    config = read_config()
    defaults = config.get("agents", {}).get("defaults", {})
    return jsonify({"model": defaults.get("model", ""), "provider": defaults.get("provider", "")})

@app.route("/api/update", methods=["POST"])
def api_update():
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
        return jsonify({"success": True, "message": f"✅ Config mise à jour : {provider} / {model}"})
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
            return jsonify({"success": False, "error": "Container nanobot-gateway introuvable"}), 404

        # 2. Restart via l'API
        r = requests.post(f"{DOCKER_PROXY_URL}/containers/{container_id}/restart", timeout=30)
        if r.status_code in (204, 200):
            return jsonify({"success": True, "message": "🔄 Container nanobot-gateway restarté avec succès"})
        return jsonify({"success": False, "error": f"HTTP {r.status_code}: {r.text}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8899, debug=False)