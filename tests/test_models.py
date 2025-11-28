"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from synchromcp.models import McpServer, McpServersConfig


class TestMcpServer:
    """Tests for McpServer model."""

    def test_stdio_server(self):
        """Test creating a stdio-based server."""
        server = McpServer(command="npx", args=["-y", "@pkg/server"])
        assert server.command == "npx"
        assert server.args == ["-y", "@pkg/server"]
        assert server.url is None

    def test_http_server(self):
        """Test creating an HTTP-based server."""
        server = McpServer(url="https://example.com/mcp")
        assert server.url == "https://example.com/mcp"
        assert server.command is None

    def test_requires_command_or_url(self):
        """Test that either command or url is required."""
        with pytest.raises(ValidationError):
            McpServer()

    def test_with_env(self):
        """Test server with environment variables."""
        server = McpServer(
            command="python",
            args=["server.py"],
            env={"API_KEY": "secret"},
        )
        assert server.env == {"API_KEY": "secret"}

    def test_disabled_field(self):
        """Test disabled field handling."""
        server = McpServer(command="test", disabled=True)
        assert server.is_disabled() is True

        server = McpServer(command="test", disabled=False)
        assert server.is_disabled() is False

    def test_enabled_field(self):
        """Test enabled field handling."""
        server = McpServer(command="test", enabled=False)
        assert server.is_disabled() is True

        server = McpServer(command="test", enabled=True)
        assert server.is_disabled() is False

    def test_extra_fields_allowed(self):
        """Test that extra fields are preserved."""
        server = McpServer(command="test", customField="value")
        assert server.model_extra.get("customField") == "value"

    def test_args_string_to_list(self):
        """Test that string args are converted to list."""
        server = McpServer(command="test", args="single-arg")
        assert server.args == ["single-arg"]

    def test_to_toml_dict(self):
        """Test conversion to TOML-compatible dict."""
        server = McpServer(
            command="npx",
            args=["-y", "pkg"],
            alwaysAllow=["tool1"],
        )
        toml_dict = server.to_toml_dict()
        assert "command" in toml_dict
        assert "always_allow" in toml_dict  # camelCase -> snake_case


class TestMcpServersConfig:
    """Tests for McpServersConfig model."""

    def test_from_dict(self):
        """Test creating config from raw dict."""
        data = {
            "server1": {"command": "npx", "args": ["-y", "pkg1"]},
            "server2": {"url": "https://example.com/mcp"},
        }
        config = McpServersConfig.from_dict(data)
        assert len(config.servers) == 2
        assert "server1" in config.servers
        assert "server2" in config.servers

    def test_to_dict(self):
        """Test converting config to dict."""
        config = McpServersConfig.from_dict(
            {
                "server1": {"command": "test", "disabled": True},
            }
        )
        result = config.to_dict()
        assert "server1" in result
        assert result["server1"]["command"] == "test"
        assert result["server1"]["disabled"] is True

    def test_to_toml_dict(self):
        """Test converting config to TOML dict."""
        config = McpServersConfig.from_dict(
            {
                "server1": {"command": "test", "alwaysAllow": ["tool1"]},
            }
        )
        result = config.to_toml_dict()
        assert "server1" in result
        assert "always_allow" in result["server1"]

    def test_empty_config(self):
        """Test creating empty config."""
        config = McpServersConfig.from_dict({})
        assert len(config.servers) == 0
