"""Tests for nanobot-manager Flask application."""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the Flask app
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app, read_config, write_config, get_ollama_models


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        with patch("app.CONFIG_PATH", str(config_file)):
            with app.test_client() as client:
                yield client


@pytest.fixture
def sample_config():
    """Return a sample configuration."""
    return {
        "agents": {
            "defaults": {
                "model": "gpt-4",
                "provider": "openai",
                "maxTokens": 8192,
                "temperature": 0.7,
            },
            "coder": {
                "model": "qwen3.5:9b-16k",
                "provider": "custom",
                "maxTokens": 16384,
                "temperature": 0.1,
            },
            "vision": {"model": "llava", "provider": "custom"},
        },
        "nanobot-manager": {"execution_type": "docker"},
    }


class TestIndexRoute:
    """Tests for the main index route."""

    @patch("app.get_ollama_models")
    def test_index_page_loads(self, mock_models, client):
        """Test that the index page loads successfully."""
        mock_models.return_value = []
        response = client.get("/")
        assert response.status_code == 200
        assert b"Nanobot Manager" in response.data
        assert b"nanobot" in response.data.lower()


class TestConfigEndpoints:
    """Tests for configuration-related endpoints."""

    def test_get_config_empty(self, client):
        """Test getting config when file doesn't exist."""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "model" in data
        assert "provider" in data
        assert "maxTokens" in data
        assert "temperature" in data

    def test_get_config_with_data(self, client, sample_config):
        """Test getting config with existing data."""
        # Write sample config
        with patch("app.read_config", return_value=sample_config):
            response = client.get("/api/config")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["model"] == "gpt-4"
            assert data["provider"] == "openai"
            assert data["maxTokens"] == 8192
            assert data["temperature"] == 0.7

    def test_update_config_success(self, client):
        """Test updating configuration successfully."""
        response = client.post(
            "/api/update",
            data=json.dumps({"model": "gpt-3.5-turbo", "provider": "openai"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_update_config_with_maxtokens_and_temperature(self, client):
        """Test updating config with maxTokens and temperature."""
        response = client.post(
            "/api/update",
            data=json.dumps(
                {
                    "model": "gpt-4",
                    "provider": "openai",
                    "maxTokens": 32768,
                    "temperature": 0.5,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify values were saved
        response = client.get("/api/config")
        data = json.loads(response.data)
        assert data["maxTokens"] == 32768
        assert data["temperature"] == 0.5

    def test_update_config_invalid_maxtokens(self, client):
        """Test updating config with invalid maxTokens."""
        response = client.post(
            "/api/update",
            data=json.dumps(
                {
                    "model": "gpt-4",
                    "provider": "openai",
                    "maxTokens": "invalid",
                    "temperature": 0.5,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_config_invalid_temperature(self, client):
        """Test updating config with invalid temperature."""
        response = client.post(
            "/api/update",
            data=json.dumps(
                {
                    "model": "gpt-4",
                    "provider": "openai",
                    "maxTokens": 8192,
                    "temperature": 3.0,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_config_missing_fields(self, client):
        """Test updating config with missing fields."""
        response = client.post(
            "/api/update",
            data=json.dumps({"model": "", "provider": "openai"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False


class TestCoderEndpoints:
    """Tests for Coder agent endpoints."""

    def test_get_coder_config(self, client, sample_config):
        """Test getting Coder configuration."""
        with patch("app.read_config", return_value=sample_config):
            response = client.get("/api/coder")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["model"] == "qwen3.5:9b-16k"
            assert data["provider"] == "custom"
            assert data["maxTokens"] == 16384

    def test_update_coder_success(self, client):
        """Test updating Coder configuration."""
        response = client.post(
            "/api/coder/update",
            data=json.dumps(
                {"model": "claude-3-opus", "provider": "anthropic", "maxTokens": 32768}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_update_coder_invalid_maxtokens(self, client):
        """Test updating Coder with invalid maxTokens."""
        response = client.post(
            "/api/coder/update",
            data=json.dumps(
                {"model": "test", "provider": "test", "maxTokens": "invalid"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestProvidersEndpoints:
    """Tests for providers endpoints."""

    def test_get_providers_list(self, client):
        """Test getting list of all providers with status."""
        config_with_providers = {
            "providers": {
                "custom": {"apiKey": ""},
                "openai": {"apiKey": "sk-test"},
            }
        }
        with patch("app.read_config", return_value=config_with_providers):
            response = client.get("/api/providers")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "providers" in data
            assert len(data["providers"]) > 0

            for provider in data["providers"]:
                assert "name" in provider
                assert "configured" in provider
                assert isinstance(provider["configured"], bool)

    def test_get_providers_custom_always_configured(self, client):
        """Test that 'custom' provider is always considered configured."""
        config_with_custom = {
            "providers": {
                "custom": {"apiKey": ""},
            }
        }
        with patch("app.read_config", return_value=config_with_custom):
            response = client.get("/api/providers")
            assert response.status_code == 200
            data = json.loads(response.data)

            custom_provider = next(
                (p for p in data["providers"] if p["name"] == "custom"), None
            )
            assert custom_provider is not None
            assert custom_provider["configured"] is True

    def test_get_providers_with_configured_provider(self, client):
        """Test providers status when one has API key configured."""
        config_with_provider = {
            "providers": {
                "openai": {"apiKey": "sk-test123", "apiBase": None},
                "anthropic": {"apiKey": "", "apiBase": None},
            }
        }

        with patch("app.read_config", return_value=config_with_provider):
            response = client.get("/api/providers")
            assert response.status_code == 200
            data = json.loads(response.data)

            openai = next((p for p in data["providers"] if p["name"] == "openai"), None)
            anthropic = next(
                (p for p in data["providers"] if p["name"] == "anthropic"), None
            )

            assert openai is not None
            assert openai["configured"] is True
            assert anthropic is not None
            assert anthropic["configured"] is False


class TestVisionEndpoints:
    """Tests for Vision agent endpoints."""

    def test_get_vision_config(self, client, sample_config):
        """Test getting Vision configuration."""
        with patch("app.read_config", return_value=sample_config):
            response = client.get("/api/vision")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["model"] == "llava"
            assert data["provider"] == "custom"

    def test_update_vision_with_maxtokens(self, client):
        """Test updating Vision with maxTokens."""
        response = client.post(
            "/api/vision/update",
            data=json.dumps(
                {"model": "gpt-4-vision", "provider": "openai", "maxTokens": 8192}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_update_vision_optional_maxtokens(self, client):
        """Test updating Vision without maxTokens."""
        response = client.post(
            "/api/vision/update",
            data=json.dumps({"model": "llava", "provider": "custom"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True


class TestExecutionTypeEndpoints:
    """Tests for execution type endpoints."""

    def test_get_execution_type(self, client, sample_config):
        """Test getting execution type."""
        with patch("app.read_config", return_value=sample_config):
            response = client.get("/api/execution-type")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["execution_type"] == "docker"

    def test_update_execution_type_success(self, client):
        """Test updating execution type."""
        with patch(
            "app.MANAGER_CONFIG_PATH",
            str(Path(tempfile.gettempdir()) / "test_manager.json"),
        ):
            response = client.post(
                "/api/execution-type/update",
                data=json.dumps({"execution_type": "host"}),
                content_type="application/json",
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True

    def test_update_execution_type_invalid(self, client):
        """Test updating execution type with invalid value."""
        response = client.post(
            "/api/execution-type/update",
            data=json.dumps({"execution_type": "invalid"}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestModelsEndpoint:
    """Tests for the Ollama models endpoint."""

    @patch("app.requests.get")
    def test_get_models_success(self, mock_get, client):
        """Test getting Ollama models successfully."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "models": [{"name": "llama2"}, {"name": "mistral"}]
        }
        mock_get.return_value = mock_response

        response = client.get("/api/models")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "llama2" in data
        assert "mistral" in data

    @patch("app.requests.get")
    def test_get_models_ollama_error(self, mock_get, client):
        """Test getting models when Ollama is unavailable."""
        mock_get.side_effect = Exception("Connection refused")

        response = client.get("/api/models")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []


class TestSshKeyEndpoints:
    """Tests for SSH key management endpoints."""

    @patch("app.get_ssh_public_key")
    def test_get_ssh_key_exists(self, mock_get_key, client):
        """Test getting SSH key when it exists."""
        mock_get_key.return_value = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI..."

        response = client.get("/api/ssh-key")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["exists"] is True
        assert "ssh-ed25519" in data["public_key"]

    @patch("app.get_ssh_public_key")
    def test_get_ssh_key_missing(self, mock_get_key, client):
        """Test getting SSH key when it doesn't exist."""
        mock_get_key.return_value = None

        response = client.get("/api/ssh-key")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["exists"] is False
        assert data["public_key"] is None

    @patch("app.generate_ssh_key")
    def test_generate_ssh_key_success(self, mock_generate, client):
        """Test generating SSH key successfully."""
        mock_generate.return_value = (True, "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...")

        response = client.post("/api/ssh-key/generate")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "public_key" in data

    @patch("app.generate_ssh_key")
    def test_generate_ssh_key_failure(self, mock_generate, client):
        """Test SSH key generation failure."""
        mock_generate.return_value = (False, "ssh-keygen not found")

        response = client.post("/api/ssh-key/generate")
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data


class TestRestartEndpoint:
    """Tests for the restart endpoint."""

    @patch("app.requests.get")
    @patch("app.requests.post")
    def test_restart_docker_success(self, mock_post, mock_get, client):
        """Test restarting via Docker API."""
        # Mock container list
        mock_get_response = MagicMock()
        mock_get_response.ok = True
        mock_get_response.json.return_value = [
            {"Names": ["/nanobot-gateway"], "Id": "abc123"}
        ]
        mock_get.return_value = mock_get_response

        # Mock restart
        mock_post_response = MagicMock()
        mock_post_response.status_code = 204
        mock_post.return_value = mock_post_response

        response = client.post("/api/restart")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    @patch("app.requests.get")
    def test_restart_container_not_found(self, mock_get, client):
        """Test restart when container is not found."""
        mock_get_response = MagicMock()
        mock_get_response.ok = True
        mock_get_response.json.return_value = []
        mock_get.return_value = mock_get_response

        response = client.post("/api/restart")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False


class TestLogsEndpoint:
    """Tests for the logs endpoint."""

    @patch("app.requests.get")
    def test_get_logs_docker_success(self, mock_get, client):
        """Test getting logs from Docker."""
        # Mock container list
        mock_response1 = MagicMock()
        mock_response1.ok = True
        mock_response1.json.return_value = [
            {"Names": ["/nanobot-gateway"], "Id": "abc123"}
        ]

        # Mock logs
        mock_response2 = MagicMock()
        mock_response2.ok = True
        mock_response2.text = "Log line 1\nLog line 2"

        mock_get.side_effect = [mock_response1, mock_response2]

        response = client.get("/api/logs")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "Log line 1" in data["logs"]

    def test_get_logs_host_mode(self, client, sample_config):
        """Test getting logs in host mode."""
        sample_config["nanobot-manager"]["execution_type"] = "host"

        with patch("app.read_config", return_value=sample_config):
            with patch("app.HOST_SSH_USER", ""):
                response = client.get("/api/logs")
                assert response.status_code == 500
                data = json.loads(response.data)
                assert data["success"] is False


class TestConfigFunctions:
    """Tests for configuration utility functions."""

    def test_read_config_returns_default_when_missing(self, client):
        """Test that read_config returns default config if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            with patch("app.CONFIG_PATH", str(config_path)):
                config = read_config()
                assert "agents" in config
                assert "defaults" in config["agents"]
                assert config_path.exists() is False

    def test_write_and_read_config(self, client):
        """Test writing and reading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            test_config = {"agents": {"defaults": {"model": "test"}}}

            with patch("app.CONFIG_PATH", str(config_path)):
                write_config(test_config)
                read_back = read_config()
                assert read_back["agents"]["defaults"]["model"] == "test"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_json_in_request(self, client):
        """Test handling invalid JSON in request body."""
        response = client.post(
            "/api/update", data="invalid json", content_type="application/json"
        )
        assert response.status_code == 400

    def test_missing_content_type(self, client):
        """Test request without proper content type."""
        response = client.post("/api/update", data=json.dumps({"model": "test"}))
        assert response.status_code == 415  # Unsupported Media Type

    def test_get_models_network_error(self, client):
        """Test handling network errors when fetching models."""
        with patch("app.requests.get", side_effect=Exception("Network error")):
            response = client.get("/api/models")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
