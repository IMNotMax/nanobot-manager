# Agent Guidelines for Nanobot Manager

## Project Overview

**Tech Stack**: Python 3.12 + Flask  
**Package Manager**: pip  
**Linter/Formatter**: Ruff  
**Deployment**: Docker with socket-proxy pattern

---

## Build & Development Commands

### Setup
```bash
# Install dependencies
pip install -r nanobot-manager/requirements.txt

# Build Docker image
docker compose build

# Run container
docker compose up -d
docker compose logs -f nanobot-manager
```

### Linting & Formatting
```bash
# Format code with Ruff
ruff format nanobot-manager/app/

# Check for lint issues
ruff check nanobot-manager/app/
```

### Testing
```bash
# Install test dependencies (if not in requirements.txt)
pip install pytest pytest-flask

# Run all tests
pytest nanobot-manager/tests/ -v

# Run single test file
pytest nanobot-manager/tests/test_app.py -v

# Run single test function
pytest nanobot-manager/tests/test_app.py::test_api_models -v

# Run with coverage
pytest nanobot-manager/tests/ --cov=nanobot-manager/app --cov-report=term-missing
```

---

## Code Style Guidelines

### Imports (PEP 8 Order)
```python
# Standard library
import json
import os
import subprocess
from typing import Union, Tuple

# Third-party
from flask import Flask, render_template, request, jsonify
import requests

# Local imports (if applicable)
from config import read_config
```

### Type Hints & Docstrings
All functions must have type hints and docstrings:
```python
def get_ollama_models(timeout: float = 5) -> list[str]:
    """Fetch available models from Ollama API.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        List of model names, empty list if request fails
    """
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []
```

### Naming Conventions
- **Functions/methods**: `snake_case` (e.g., `read_config`, `api_update`)
- **Classes**: `PascalCase` (e.g., `ConfigManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CONFIG_PATH`, `OLLAMA_URL`)
- **Variables**: `snake_case` (e.g., `max_tokens`, `container_id`)
- **Private**: `_prefix_lowercase` (e.g., `_internal_helper`)

### Error Handling
Catch specific exceptions, provide informative messages:
```python
@app.route("/api/update", methods=["POST"])
def api_update():
    try:
        data = request.json
        model = data.get("model", "").strip()
        provider = data.get("provider", "").strip()
        
        # Validate input
        if not model or not provider:
            return jsonify({"success": False, "error": "Model and provider required"}), 400
        
        # Business logic
        config = read_config()
        config["agents"]["defaults"] = {"model": model, "provider": provider}
        write_config(config)
        
        return jsonify({"success": True, "message": f"Updated: {provider}/{model}"})
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Config file not found"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"Invalid JSON: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### API Response Format
Consistent response structure:
```python
# Success (HTTP 200)
{"success": true, "message": "✅ Config updated", "data": {...}}

# Error (HTTP 4xx or 5xx)
{"success": false, "error": "Descriptive error message"}
```

### String Formatting
Use f-strings for clarity:
```python
message = f"Config: {provider} / {model} ({max_tokens} tokens)"
```

---

## Project Structure

```
nanobot-manager/
├── app.py              # Flask app, API routes
├── requirements.txt    # Dependencies: flask>=3.0, requests>=2.31
├── Dockerfile         # Python 3.12 container
├── templates/
│   └── index.html    # Web UI
└── tests/
    ├── __init__.py
    └── test_app.py   # Unit tests
```

## Environment Variables
```bash
CONFIG_PATH=/opt/stacks/nanobot/config/config.json
OLLAMA_URL=http://ollama:11434
DOCKER_PROXY_URL=http://docker-socket-proxy:2375
HTTP_PORT=8899
```

---

## Security Best Practices
- Validate all external API responses before use
- Sanitize container names before Docker API calls
- Never commit `.env` or credentials
- Use specific exception types (avoid bare `except`)
- Validate input data types before processing

---

## Testing Standards
- Place tests in `nanobot-manager/tests/`
- Mock external services (Ollama, Docker)
- Aim for >80% coverage on API endpoints
- Use descriptive test names: `test_api_update_success`, `test_api_update_missing_fields`
