# Agent Guidelines for Nanobot Manager

**Tech Stack**: Python 3.12 + Flask | **Package Manager**: pip | **Linter**: Ruff (optional)  
**Features**: Multi-agent config, execution modes (Docker/Host via SSH), logs viewer, SSH key management

## Build & Development Commands

### Setup & Docker
```bash
pip install -r app/requirements.txt
docker compose build --no-cache
docker compose up -d
docker compose logs -f nanobot-manager
```

### Linting & Formatting (Optional)
```bash
pip install ruff
ruff format app/
ruff check app/ --fix
```

### Testing
```bash
# Install dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest app/tests/ -v

# Run single test function (important!)
pytest app/tests/test_app.py::test_api_restart_docker -v

# With coverage
pytest app/tests/ -v --cov=app --cov-report=term-missing
```

## Code Style Guidelines

### Imports (PEP 8 Order)
```python
# Standard library
import json
import os
import pathlib
import subprocess
from typing import Union, Tuple

# Third-party
from flask import Flask, render_template, request, jsonify, Response
import requests
```

### Type Hints & Docstrings (Required)
```python
def get_ssh_public_key() -> Union[str, None]:
    """Retrieve SSH public key if it exists.
    
    Returns:
        SSH public key string or None if not found
    """
    ssh_key_path = pathlib.Path("/root/.ssh/id_ed25519.pub")
    if ssh_key_path.exists():
        return ssh_key_path.read_text().strip()
    return None
```

### Naming Conventions
- **Functions/methods**: `snake_case` (e.g., `read_config`, `api_update`)
- **Classes**: `PascalCase` (e.g., `ConfigManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CONFIG_PATH`, `OLLAMA_URL`)
- **Variables**: `snake_case` (e.g., `max_tokens`, `container_id`)

### Error Handling (Never crash the UI!)
Catch specific exceptions and return JSON errors:
```python
@app.route("/api/update", methods=["POST"])
def api_update():
    try:
        data = request.json
        model = data.get("model", "").strip()
        if not model:
            return jsonify({"success": False, "error": "Model required"}), 400
        # Business logic...
        return jsonify({"success": True, "message": f"✅ Config updated: {model}"})
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Config file not found"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### API Response Format & Emojis
```python
# Success: {"success": True, "message": "✅ Updated"}
# Error: {"success": False, "error": "Descriptive message"}
# Use f-strings: f"🔄 Mode changed: {type}"
```

## Project Structure & Key Details

```
nanobot-manager/app/
├── app.py              # Flask app with all API endpoints
├── requirements.txt    # flask>=3.0, requests>=2.31
├── templates/index.html
└── tests/test_app.py
```

### Execution Modes (Docker vs Host)
- **Docker**: Uses Docker Socket Proxy API (`/api/restart`)
- **Host**: Uses SSH + `systemctl --user restart nanobot-gateway`
- Config: `system.execution_type` field

### Important API Endpoints
- `GET/POST /api/execution-type` - Get/set execution mode
- `POST /api/restart` - Restart (adapts to mode)
- `GET/POST /api/ssh-key` - SSH key management
- `GET /api/logs` - Fetch logs (Docker API or SSH+journalctl)

### Subprocess & SSH Best Practices
- Always use list format: `subprocess.run(["ssh", "-p", str(port), ...], ...)`
- Set `capture_output=True, text=True, timeout=30`
- Catch `subprocess.TimeoutExpired` explicitly
- Use `pathlib.Path()` for file operations
- SSH keys: ed25519 format, stored in `/root/.ssh/id_ed25519.pub`

## Security & Testing
- Validate all external API responses
- Use specific exception types (never bare `except`)
- Test both success & error paths
- Mock Ollama, Docker, SSH in tests
- Place tests in `app/tests/`
- Never commit `.env` or credentials
