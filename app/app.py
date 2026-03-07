from flask import Flask, render_template, request, jsonify, Response
from typing import Union, Tuple
import json
import subprocess
import requests
import os
import pathlib

app = Flask(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/root/.nanobot/config.json")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
DOCKER_PROXY_URL = os.environ.get(
    "DOCKER_PROXY_URL", "http://socket-proxy-nbt-mngr:2375"
)
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8899"))
HOST_SSH_USER = os.environ.get("HOST_SSH_USER", "")
HOST_SSH_HOST = os.environ.get("HOST_SSH_HOST", "localhost")
HOST_SSH_PORT = int(os.environ.get("HOST_SSH_PORT", "22"))


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


def get_ssh_public_key() -> Union[str, None]:
    """Retrieve SSH public key if it exists."""
    ssh_key_path = pathlib.Path("/root/.ssh/id_ed25519.pub")
    if ssh_key_path.exists():
        try:
            return ssh_key_path.read_text().strip()
        except Exception as e:
            print(f"Error reading SSH key: {e}")
    return None


def generate_ssh_key() -> Tuple[bool, str]:
    """Generate SSH key pair."""
    try:
        result = subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-f",
                "/root/.ssh/id_ed25519",
                "-N",
                "",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Read and return the public key
            public_key = get_ssh_public_key()
            return (True, public_key or "")
        else:
            return (False, f"ssh-keygen error: {result.stderr}")
    except subprocess.TimeoutExpired:
        return (False, "ssh-keygen timeout")
    except FileNotFoundError:
        return (False, "ssh-keygen not found")
    except Exception as e:
        return (False, str(e))


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


@app.route("/api/execution-type")
def api_execution_type():
    """Retrieve execution type (docker or host)."""
    try:
        config = read_config()
        execution_type = config.get("nanobot-manager", {}).get("execution_type", "docker")
        return jsonify({"execution_type": execution_type})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/execution-type/update", methods=["POST"])
def api_execution_type_update():
    """Update execution type (docker or host)."""
    data = request.json
    execution_type = data.get("execution_type", "").strip().lower()

    if execution_type not in ("docker", "host"):
        return jsonify(
            {"success": False, "error": "execution_type doit être 'docker' ou 'host'"}
        ), 400

    try:
        config = read_config()
        config.setdefault("nanobot-manager", {})
        config["nanobot-manager"]["execution_type"] = execution_type
        write_config(config)
        return jsonify(
            {
                "success": True,
                "message": f"✅ Mode d'exécution changé : {execution_type}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/restart", methods=["POST"])
def api_restart():
    try:
        config = read_config()
        execution_type = config.get("nanobot-manager", {}).get("execution_type", "docker")

        if execution_type == "host":
            # Restart using SSH + systemctl on host
            if not HOST_SSH_USER:
                return jsonify(
                    {
                        "success": False,
                        "error": "HOST_SSH_USER not configured. Set HOST_SSH_USER env var.",
                    }
                ), 500

            try:
                ssh_cmd = [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-p",
                    str(HOST_SSH_PORT),
                    f"{HOST_SSH_USER}@{HOST_SSH_HOST}",
                    "systemctl --user restart nanobot-gateway",
                ]
                result = subprocess.run(
                    ssh_cmd, capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return jsonify(
                        {
                            "success": True,
                            "message": "🔄 Service nanobot-gateway restarté avec succès",
                        }
                    )
                else:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"SSH error: {result.stderr}",
                        }
                    ), 500
            except subprocess.TimeoutExpired:
                return jsonify({"success": False, "error": "SSH restart timeout"}), 500
            except FileNotFoundError:
                return jsonify({"success": False, "error": "ssh not found"}), 500
        else:
            # Restart using Docker API
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


@app.route("/api/ssh-key")
def api_ssh_key():
    """Retrieve SSH public key if it exists."""
    try:
        public_key = get_ssh_public_key()
        return jsonify({"public_key": public_key, "exists": public_key is not None})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ssh-key/generate", methods=["POST"])
def api_ssh_key_generate():
    """Generate SSH key pair."""
    try:
        success, message = generate_ssh_key()
        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "✅ Clé SSH générée avec succès",
                    "public_key": message,
                }
            )
        else:
            return jsonify({"success": False, "error": message}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logs")
def api_logs():
    """Retrieve nanobot-gateway logs based on execution type."""
    try:
        config = read_config()
        execution_type = config.get("nanobot-manager", {}).get("execution_type", "docker")

        if execution_type == "host":
            # Get logs from host via SSH + journalctl
            if not HOST_SSH_USER:
                return jsonify(
                    {
                        "success": False,
                        "error": "HOST_SSH_USER not configured",
                        "logs": "",
                    }
                ), 500

            try:
                ssh_cmd = [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-p",
                    str(HOST_SSH_PORT),
                    f"{HOST_SSH_USER}@{HOST_SSH_HOST}",
                    "journalctl --user -u nanobot-gateway -n 100 --no-pager",
                ]
                result = subprocess.run(
                    ssh_cmd, capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return jsonify(
                        {"success": True, "logs": result.stdout, "source": "host"}
                    )
                else:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"SSH error: {result.stderr}",
                            "logs": "",
                            "source": "host",
                        }
                    ), 500
            except subprocess.TimeoutExpired:
                return jsonify(
                    {
                        "success": False,
                        "error": "SSH logs timeout",
                        "logs": "",
                        "source": "host",
                    }
                ), 500
            except FileNotFoundError:
                return jsonify(
                    {
                        "success": False,
                        "error": "ssh not found",
                        "logs": "",
                        "source": "host",
                    }
                ), 500
        else:
            # Get logs from Docker container
            try:
                resp = requests.get(
                    f"{DOCKER_PROXY_URL}/containers/json?all=1", timeout=5
                )
                resp.raise_for_status()
                containers = resp.json()
                container_id = None
                for c in containers:
                    if any("nanobot-gateway" in name for name in c.get("Names", [])):
                        container_id = c["Id"]
                        break

                if not container_id:
                    return jsonify(
                        {
                            "success": False,
                            "error": "Container nanobot-gateway not found",
                            "logs": "",
                            "source": "docker",
                        }
                    ), 404

                # Get container logs
                log_resp = requests.get(
                    f"{DOCKER_PROXY_URL}/containers/{container_id}/logs",
                    params={"stdout": 1, "stderr": 1, "tail": 100},
                    timeout=5,
                )
                if log_resp.ok:
                    return jsonify(
                        {
                            "success": True,
                            "logs": log_resp.text,
                            "source": "docker",
                        }
                    )
                else:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"Docker error: {log_resp.status_code}",
                            "logs": "",
                            "source": "docker",
                        }
                    ), 500
            except requests.exceptions.Timeout:
                return jsonify(
                    {
                        "success": False,
                        "error": "Docker logs timeout",
                        "logs": "",
                        "source": "docker",
                    }
                ), 500
            except Exception as e:
                return jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "logs": "",
                        "source": "docker",
                    }
                ), 500

    except Exception as e:
        return jsonify(
            {"success": False, "error": str(e), "logs": "", "source": "unknown"}
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)
