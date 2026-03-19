from flask import Flask, render_template, request, jsonify, Response
from typing import Union, Tuple
import json
import subprocess
import requests
import os
import pathlib

app = Flask(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.json")
MANAGER_CONFIG_PATH = os.environ.get("MANAGER_CONFIG_PATH", "/app/config/manager.json")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
DOCKER_PROXY_URL = os.environ.get(
    "DOCKER_PROXY_URL", "http://socket-proxy-nbt-mngr:2375"
)
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8899"))
HOST_SSH_USER = os.environ.get("HOST_SSH_USER", "")
HOST_SSH_HOST = os.environ.get("HOST_SSH_HOST", "localhost")
HOST_SSH_PORT = int(os.environ.get("HOST_SSH_PORT", "22"))


DEFAULT_CONFIG = {
    "agents": {
        "defaults": {
            "model": "qwen3.5:9b-16k",
            "provider": "custom",
            "maxTokens": 16384,
            "temperature": 0.1,
        },
        "coder": {"model": "qwen3.5:9b-16k", "provider": "custom", "maxTokens": 16384},
        "vision": {"model": "qwen3.5:9b-16k", "provider": "custom"},
    }
}

# Liste complète des providers supportés par Nanobot
# "custom" et "ollama" sont équivalents (Ollama local)
ALL_PROVIDERS = [
    "ollama",  # Ollama local (alias de "custom")
    "anthropic",
    "openai",
    "openrouter",
    "deepseek",
    "groq",
    "zhipu",
    "dashscope",
    "vllm",
    "gemini",
    "moonshot",
    "minimax",
    "aihubmix",
    "siliconflow",
    "volcengine",
    "openaiCodex",
    "githubCopilot",
]


def normalize_provider_name(provider_name):
    """Normalize provider name - 'custom' and 'ollama' are equivalent."""
    if not provider_name:
        return "ollama"
    provider_lower = provider_name.lower()
    if provider_lower == "custom":
        return "ollama"
    return provider_lower


def read_config():
    """Read nanobot config file. NEVER writes to this file to preserve permissions."""
    config_path = pathlib.Path(CONFIG_PATH)

    if not config_path.exists():
        print(f"WARNING: Nanobot config not found at {CONFIG_PATH}", flush=True)
        print(
            f"WARNING: Using default config. Please ensure the file exists.", flush=True
        )
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Corrupted config file at {CONFIG_PATH}: {e}", flush=True)
        print(f"ERROR: Please fix the JSON syntax manually", flush=True)
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"ERROR reading config: {e}", flush=True)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Corrupted config file at {CONFIG_PATH}: {e}")
        # Backup corrupted file
        backup_path = config_path.with_suffix(".json.corrupted")
        try:
            config_path.rename(backup_path)
            print(f"Backup created at {backup_path}")
        except Exception as backup_err:
            print(f"Failed to backup: {backup_err}")
        # Create new default config
        write_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"ERROR reading config: {e}")
        return DEFAULT_CONFIG.copy()


def write_config(config):
    """Write to nanobot config. WARNING: Should not be used as config is read-only."""
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except PermissionError:
        print(f"ERROR: Cannot write to {CONFIG_PATH} - file is read-only", flush=True)
        raise PermissionError(
            f"Cannot write to nanobot config. File is mounted read-only."
        )
    except Exception as e:
        print(f"ERROR writing config: {e}", flush=True)
        raise


def read_manager_config():
    """Read nanobot-manager specific configuration (separate from nanobot config)."""
    config_path = pathlib.Path(MANAGER_CONFIG_PATH)
    if not config_path.exists():
        # Return default config
        return {"execution_type": "docker"}
    try:
        with open(MANAGER_CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"execution_type": "docker"}


def write_manager_config(config):
    """Write nanobot-manager specific configuration."""
    config_path = pathlib.Path(MANAGER_CONFIG_PATH)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(MANAGER_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_ollama_url():
    """Get Ollama URL from config or use default."""
    try:
        config = read_config()
        providers = config.get("providers", {})
        custom_config = providers.get("custom", {})
        api_base = custom_config.get("apiBase", "")

        # If apiBase is set and contains a URL, use it
        if api_base and isinstance(api_base, str) and api_base.strip():
            # Remove trailing /v1 if present (nanobot format)
            url = api_base.rstrip("/")
            if url.endswith("/v1"):
                url = url[:-3]
            return url
    except Exception as e:
        print(f"Error reading Ollama URL from config: {e}")

    # Fall back to environment variable
    return OLLAMA_URL


def get_ollama_models():
    """Fetch available models from Ollama."""
    try:
        ollama_url = get_ollama_url()
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
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


def get_provider_status(config, provider_name):
    """Check if a provider is properly configured.

    For Ollama: always considered available (local)
    For other providers: configured only if apiKey is a non-empty string
    """
    providers = config.get("providers", {})

    # Normalize provider name
    normalized_name = normalize_provider_name(provider_name)

    # Handle Ollama - always available locally
    if normalized_name == "ollama":
        return True

    # For other providers, check if apiKey is a non-empty string
    if provider_name in providers:
        provider_config = providers[provider_name]
        api_key = provider_config.get("apiKey", "")
        # Provider is configured only if apiKey is a non-empty string
        if isinstance(api_key, str) and api_key.strip():
            return True

    return False


@app.route("/")
def index():
    config = read_config()
    defaults = config.get("agents", {}).get("defaults", {})
    # Normalize provider name for display
    provider = normalize_provider_name(defaults.get("provider", ""))
    return render_template(
        "index.html",
        current_model=defaults.get("model", ""),
        current_provider=provider,
        ollama_models=get_ollama_models(),
    )


@app.route("/api/models")
def api_models():
    return jsonify(get_ollama_models())


@app.route("/api/ollama-config")
def api_ollama_config():
    """Get Ollama configuration to determine if we can fetch models."""
    try:
        config = read_config()
        providers = config.get("providers", {})

        # Check both "ollama" and "custom" keys
        ollama_config = providers.get("ollama", providers.get("custom", {}))
        api_base = ollama_config.get("apiBase", "")

        # Check if apiBase is a valid URL
        has_url = bool(
            api_base
            and isinstance(api_base, str)
            and api_base.strip().startswith("http")
        )

        return jsonify(
            {
                "hasUrl": has_url,
                "apiBase": api_base if has_url else None,
                "canFetchModels": has_url,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/providers")
def api_providers():
    """Get all providers from nanobot config with their configuration status."""
    import sys

    try:
        config = read_config()
        providers_config = config.get("providers", {})

        sys.stdout.flush()
        print(f"DEBUG: providers_config = {providers_config}", flush=True)
        print(f"DEBUG: providers_config type = {type(providers_config)}", flush=True)
        print(
            f"DEBUG: providers_config keys = {list(providers_config.keys()) if providers_config else 'EMPTY'}",
            flush=True,
        )
        sys.stdout.flush()

        providers_status = []

        # Iterate through all providers defined in nanobot config
        for provider_name in providers_config.keys():
            is_configured = get_provider_status(config, provider_name)
            providers_status.append(
                {"name": provider_name, "configured": is_configured}
            )
            print(
                f"DEBUG: Added provider {provider_name}, configured={is_configured}",
                flush=True,
            )

        print(f"DEBUG: Returning {len(providers_status)} providers", flush=True)
        sys.stdout.flush()
        return jsonify({"providers": providers_status})
    except Exception as e:
        print(f"ERROR in api_providers: {e}", flush=True)
        import traceback

        traceback.print_exc()
        sys.stdout.flush()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config")
def api_config():
    config = read_config()
    defaults = config.get("agents", {}).get("defaults", {})
    # Normalize provider name
    provider = normalize_provider_name(defaults.get("provider", ""))
    return jsonify(
        {
            "model": defaults.get("model", ""),
            "provider": provider,
            "maxTokens": defaults.get("maxTokens", 16384),
            "temperature": defaults.get("temperature", 0.1),
        }
    )


@app.route("/api/update", methods=["POST"])
def api_update():
    """Update default agent configuration (model, provider, maxTokens, temperature)."""
    data = request.json
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()
    max_tokens = data.get("maxTokens", 16384)
    temperature = data.get("temperature", 0.1)

    if not model or not provider:
        return jsonify({"success": False, "error": "Champs requis"}), 400

    try:
        max_tokens = int(max_tokens)
        if max_tokens <= 0:
            return jsonify({"success": False, "error": "maxTokens doit être > 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "maxTokens invalide"}), 400

    try:
        temperature = float(temperature)
        if not 0 <= temperature <= 2:
            return jsonify(
                {"success": False, "error": "temperature doit être entre 0 et 2"}
            ), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "temperature invalide"}), 400

    # NOTE: Writing to nanobot config is disabled to preserve file permissions
    # Config changes must be made manually on the host
    return jsonify(
        {
            "success": False,
            "error": "Modification du fichier nanobot désactivée pour préserver les permissions. Veuillez modifier le fichier ~/.nanobot/config.json manuellement sur l'hôte.",
        }
    ), 403


@app.route("/api/config/full")
def api_config_full():
    """Get full configuration including all agents settings."""
    try:
        config = read_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/advanced", methods=["POST"])
def api_config_advanced():
    """Update advanced configuration settings."""
    data = request.json
    workspace = data.get("workspace", "~/.nanobot/workspace").strip()
    max_tool_iterations = data.get("maxToolIterations", 40)
    memory_window = data.get("memoryWindow", 100)
    reasoning_effort = data.get("reasoningEffort")
    mcp_servers = data.get("mcpServers", [])

    try:
        max_tool_iterations = int(max_tool_iterations)
        if max_tool_iterations <= 0 or max_tool_iterations > 100:
            return jsonify(
                {
                    "success": False,
                    "error": "maxToolIterations doit être entre 1 et 100",
                }
            ), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "maxToolIterations invalide"}), 400

    try:
        memory_window = int(memory_window)
        if memory_window < 10 or memory_window > 500:
            return jsonify(
                {"success": False, "error": "memoryWindow doit être entre 10 et 500"}
            ), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "memoryWindow invalide"}), 400

    try:
        config = read_config()
        config.setdefault("agents", {}).setdefault("defaults", {})
        config["agents"]["defaults"]["workspace"] = workspace
        config["agents"]["defaults"]["maxToolIterations"] = max_tool_iterations
        config["agents"]["defaults"]["memoryWindow"] = memory_window
        if reasoning_effort:
            config["agents"]["defaults"]["reasoningEffort"] = reasoning_effort
        elif "reasoningEffort" in config["agents"]["defaults"]:
            del config["agents"]["defaults"]["reasoningEffort"]
        config["agents"]["defaults"]["mcpServers"] = mcp_servers
        write_config(config)
        return jsonify(
            {"success": True, "message": "✅ Configuration avancée mise à jour"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/provider/config", methods=["POST"])
def api_provider_config():
    """Configure a provider (apiKey, apiBase, extraHeaders)."""
    data = request.json
    provider = data.get("provider", "").strip()
    api_key = data.get("apiKey", "")
    api_base = data.get("apiBase")
    extra_headers = data.get("extraHeaders")

    if not provider:
        return jsonify({"success": False, "error": "Provider requis"}), 400

    try:
        config = read_config()
        config.setdefault("providers", {})

        # If apiKey is empty, remove the provider config
        if not api_key.strip():
            if provider in config["providers"]:
                del config["providers"][provider]
                write_config(config)
                return jsonify(
                    {"success": True, "message": f"✅ Provider '{provider}' supprimé"}
                )
            else:
                return jsonify(
                    {"success": False, "error": f"Provider '{provider}' non trouvé"}
                ), 404

        # Update or create provider config
        config["providers"][provider] = {"apiKey": api_key}

        if api_base:
            config["providers"][provider]["apiBase"] = api_base

        if extra_headers:
            config["providers"][provider]["extraHeaders"] = extra_headers

        write_config(config)
        return jsonify(
            {"success": True, "message": f"✅ Provider '{provider}' configuré"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/provider/config", methods=["DELETE"])
def api_provider_config_delete():
    """Delete a provider configuration."""
    data = request.json
    provider = data.get("provider", "").strip()

    if not provider:
        return jsonify({"success": False, "error": "Provider requis"}), 400

    try:
        config = read_config()

        if provider not in config.get("providers", {}):
            return jsonify(
                {"success": False, "error": f"Provider '{provider}' non trouvé"}
            ), 404

        del config["providers"][provider]
        write_config(config)
        return jsonify(
            {"success": True, "message": f"✅ Provider '{provider}' supprimé"}
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
    """Retrieve execution type (docker or host) from manager config."""
    try:
        config = read_manager_config()
        execution_type = config.get("execution_type", "docker")
        return jsonify({"execution_type": execution_type})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/execution-type/update", methods=["POST"])
def api_execution_type_update():
    """Update execution type (docker or host) in manager config."""
    data = request.json
    execution_type = data.get("execution_type", "").strip().lower()

    if execution_type not in ("docker", "host"):
        return jsonify(
            {"success": False, "error": "execution_type doit être 'docker' ou 'host'"}
        ), 400

    try:
        config = read_manager_config()
        config["execution_type"] = execution_type
        write_manager_config(config)
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
        config = read_manager_config()
        execution_type = config.get("execution_type", "docker")

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
        config = read_manager_config()
        execution_type = config.get("execution_type", "docker")

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
