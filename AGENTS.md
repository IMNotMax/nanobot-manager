# Agent Guidelines for Nanobot Manager

## Project Overview

**Tech Stack**: Python 3.12 + Flask
**Deployment**: Docker with socket-proxy pattern
**Service Discovery**: Ollama API integration
**Testing**: pytest with fixtures and mocking

---

## Build & Development Commands

### Environment Setup
```bash
pip install -r nanobot-manager/requirements.txt
```

### Docker Management
```bash
docker network create socket-proxy-network
docker compose -f compose.yaml build
docker compose -f compose.yaml up -d
docker compose -f compose.yaml down
```

### Linting & Formatting (ruff)
```bash
ruff format nanobot-manager/
ruff check nanobot-manager/ --fix
```

### Testing (pytest)
```bash
pytest nanobot-manager/tests/                 # All tests
pytest nanobot-manager/tests/test_app.py      # Single file
pytest nanobot-manager/tests/test_app.py::TestConfigEndpoints -v  # Single class
pytest nanobot-manager/tests/test_app.py::TestConfigEndpoints::test_update_config_success -v  # Single test
```

---

## Code Style Guidelines

### Imports (PEP 8 Order)
```python
import json
import os
import subprocess
from pathlib import Path

import requests
from flask import Flask, render_template, request, jsonify

from app import app, read_config, get_ollama_models
```

### Type Hints
All function signatures must include type hints:
```python
def read_config() -> dict:
    """Read nanobot config file."""

def get_ollama_models() -> list[str]:
    """Fetch available models from Ollama."""

def get_ssh_key_path() -> str:
    """Get the SSH private key path."""

def generate_ssh_key() -> Tuple[bool, str]:
    """Generate SSH key pair."""
```

### Naming Conventions
- **Functions/methods**: snake_case (`read_config`, `get_ollama_models`)
- **Classes**: PascalCase (`TestConfigEndpoints`, `TestModelsEndpoint`)
- **Constants**: UPPER_SNAKE_CASE (`CONFIG_PATH`, `OLLAMA_URL`, `ALL_PROVIDERS`)
- **Variables**: snake_case (`is_configured`, `container_id`, `execution_type`)
- **Private**: single underscore prefix (`_internal_helper`)

### Error Handling Best Practices
```python
try:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
except requests.Timeout:
    logging.warning("Request timed out")
except requests.ConnectionError:
    logging.error("Connection failed")
except Exception as e:
    logging.exception("Unexpected error occurred")
    raise
```

Always return informative JSON errors from API endpoints:
```python
@app.route("/api/endpoint")
def api_endpoint():
    try:
        return jsonify({"success": True, "data": result})
    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### Input Validation
Validate all incoming data before processing:
```python
@app.route("/api/update", methods=["POST"])
def api_update():
    data = request.json
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()

    if not model or not provider:
        return jsonify({"success": False, "error": "Champs requis"}), 400

    try:
        max_tokens = int(data.get("maxTokens", 16384))
        if max_tokens <= 0:
            return jsonify({"success": False, "error": "maxTokens doit être > 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "maxTokens invalide"}), 400
```

### Return Type Consistency
API endpoints must consistently return:
- **Success**: `{"success": True, "message": "..."}` (HTTP 200)
- **Error**: `{"success": False, "error": "..."}` (HTTP 400/403/500)

### String Formatting
```python
message = f"Config updated: {provider} / {model}"
```

---

## Testing Guidelines

### Test Structure (pytest)
```python
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app, read_config

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

class TestConfigEndpoints:
    def test_get_config_empty(self, client):
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_update_config_success(self, client):
        response = client.post(
            "/api/update",
            data=json.dumps({"model": "gpt-3.5", "provider": "openai"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
```

### Mocking External Services
```python
@patch("app.requests.get")
def test_get_models_success(self, mock_get, client):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"models": [{"name": "llama2"}]}
    mock_get.return_value = mock_response

    response = client.get("/api/models")
    assert response.status_code == 200

@patch("app.get_ollama_models")
def test_index_page_loads(self, mock_models, client):
    mock_models.return_value = []
    response = client.get("/")
    assert response.status_code == 200
```

---

## Project Structure

```
nanobot-manager/
├── nanobot-manager/
│   ├── app.py              # Flask application (routes API)
│   ├── requirements.txt     # Dependencies: flask>=3.0, requests>=2.31
│   ├── Dockerfile           # Docker image
│   └── templates/
│       └── index.html       # Web interface
├── nanobot-manager/tests/
│   └── test_app.py          # pytest tests
├── compose.yaml             # Docker Compose config
├── .env.example             # Environment template
└── AGENTS.md                # This file
```

---

## Configuration Files

### nanobot config.json (read-only)
Managed by nanobot, mounted at `~/.nanobot/config.json`. Structure:
```json
{
  "providers": { "custom": {"apiKey": "...", "apiBase": "..."} },
  "agents": {
    "defaults": {"model": "qwen3.5:9b-16k", "provider": "custom"},
    "coder": {"model": "...", "provider": "...", "maxTokens": 16384},
    "vision": {"model": "...", "provider": "..."}
  }
}
```

### manager.json (read/write)
Nanobot-manager's own config at `/app/config/manager.json`:
```json
{"execution_type": "docker"}
```

---

## Supported Providers
```python
ALL_PROVIDERS = [
    "ollama", "custom", "anthropic", "openai", "openrouter", "deepseek",
    "groq", "zhipu", "dashscope", "vllm", "gemini", "moonshot", "minimax",
    "aihubmix", "siliconflow", "volcengine", "openaiCodex", "githubCopilot"
]
```

---

## Docker & Infrastructure

### Network Setup
- Container `nanobot-manager` connects to `socket-proxy-network`
- Docker socket exposed via `socket-proxy` container on port 2375
- Ollama service runs locally and is discoverable via Docker network

### Environment Variables
- `CONFIG_PATH=/home/app/.nanobot/config.json`
- `MANAGER_CONFIG_PATH=/app/config/manager.json`
- `OLLAMA_URL=http://ollama:11434`
- `DOCKER_PROXY_URL=http://socket-proxy:2375`
- `HTTP_PORT=8899`
- `HOST_SSH_USER`, `HOST_SSH_HOST`, `HOST_SSH_PORT` for host mode

---

## Security Checklist

- Never commit `.env` files with credentials
- Validate all external API responses before use
- Sanitize container names before Docker API calls
- Use specific exception types over bare `except:`
- Validate input ranges (e.g., 0 <= temperature <= 2)

---

## Documentation

- `README.md`: User-facing documentation
- `FEATURES.md`: Detailed feature documentation
- `TESTING_GUIDE.md`: Manual testing procedures
- Function docstrings: Required for public APIs
- This file: Agent development guidelines

**Testing**: Tests should mock external services (Ollama, Docker API) with `unittest.mock.patch`.
