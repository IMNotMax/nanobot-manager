# Agent Guidelines for Nanobot Manager

## Project Overview

**Tech Stack**: Python 3.12 + Flask  
**Deployment**: Docker with socket-proxy pattern  
**Service Discovery**: Ollama API integration

---

## Build & Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r nanobot-manager/requirements.txt

# Or within the container:
docker build -f nanobot-manager/Dockerfile -t nanobot-manager:dev .
```

### Docker Management
```bash
# Create socket network
docker network create socket-proxy-network

# Build/rebuild image
docker compose -f compose.yaml build

# Run in detached mode
docker compose -f compose.yaml up -d

# Stop container
docker compose -f compose.yaml down
```

### Linting & Formatting
```bash
# Format code with ruff
ruff format nanobot-manager/

# Check lint issues
ruff check nanobot-manager/
```

### Testing
```bash
# Run tests (using pytest)
pytest nanobot-manager/tests/

# Run a single test file
pytest nanobot-manager/tests/test_app.py

# Run a single test function
pytest nanobot-manager/tests/test_app.py::test_api_models -v
```

**Test structure** - place tests in `nanobot-manager/tests/`:
```python
import unittest
from flask import Flask
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_api_models(self):
        response = self.client.get('/api/models')
        assert response.status_code == 200
```

---

## Code Style Guidelines

### Imports (PEP 8 Order)
```python
# Standard library imports come first
import json
import os
import subprocess

# Third-party imports second
from flask import Flask, render_template, request, jsonify
import requests

# Local module imports last
from .modules import helper_function
```

### Type Hints
All function signatures must include type hints:
```python
def read_config() -> ConfigData:
    """Read config file and return parsed data."""

def get_ollama_models(timeout: float = 5) -> list[str]:
    """Fetch Ollama models with configurable timeout."""
```

### Naming Conventions
- **Functions/methods**: snake_case (e.g., `read_config`, `get_ollama_models`)
- **Classes**: PascalCase (e.g., `ConfigManager`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `CONFIG_PATH`, `OLLAMA_URL`)
- **Variables**: snake_case (e.g., `is_configured`, `container_id`)
- **Private**: single underscore prefix (e.g., `_internal_helper`)

### Error Handling Best Practices
```python
# Catch specific exceptions, not bare except
try:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
except requests.Timeout:
    logging.warning("Request timed out")
except requests.ConnectionError:
    logging.error("Connection failed")
except Exception as e:  # Catch-all for unexpected errors
    logging.exception("Unexpected error occurred")
    raise  # Re-raise if recovery isn't possible
```

Always include informative error messages to clients:
```python
def api_endpoint():
    try:
        # ... business logic ...
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### Input Validation
Validate all incoming data before processing:
```python
def update_config(data: dict) -> dict:
    model = data.get("model", "").strip()
    provider = data.get("provider", "").strip()
    
    if not model or not provider:
        return {"success": False, "error": "Champs requis"}, 400
    
    # Proceed with updates...
    return {"success": True, "message": "Config updated"}
```

### Return Type Consistency
API endpoints must consistently return:
- **Success**: `{"success": True, "message": "..."}` (HTTP 200)
- **Error**: `{"success": False, "error": "..."}` (HTTP 500)

### String Formatting
Use f-strings with explicit type conversion for complex types:
```python
# Prefer:
message = f"Config updated: {model} / {provider}"

# Avoid unnecessary conversions:
bad = f"{value}"  # if value is already a string
```

---

## Docker & Infrastructure Notes

### Network Setup
- Container `nanobot-gateway` connects to `socket-proxy-network`
- Docker socket exposed via proxy container on port 2375
- Ollama service runs locally and is discoverable via Docker network

### Environment Variables (Optional Override)
- `CONFIG_PATH=/opt/stacks/nanobot/config/config.json`
- `OLLAMA_URL=http://ollama:11434`
- `DOCKER_PROXY_URL=http://docker-socket-proxy:2375`

---

## Security Checklist

- [ ] Never commit `.env` files with credentials
- [ ] Validate all external API responses before use
- [ ] Use HTTPS in production (consider environment-based URL switching)
- [ ] Sanitize container names before API calls
- [ ] Rate limit external requests to prevent DoS

---

## Documentation

- README.md: User-facing documentation
- This file: Agent development guidelines
- Function docstrings: Required for public APIs

**Testing**: Tests should mock external services (Ollama, Docker API) and aim for >80% coverage on API endpoints.
