"""Tests for file readers."""

import json

from synchromcp.config import ConfigLocation, FileType, McpKey
from synchromcp.readers import (
    extract_mcp_servers,
    read_config,
    read_json,
)


class TestReadJson:
    """Tests for JSON reading."""

    def test_read_valid_json(self, tmp_path):
        """Test reading valid JSON file."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"key": "value", "number": 42}')

        data = read_json(config_file)
        assert data["key"] == "value"
        assert data["number"] == 42

    def test_read_json_with_unicode(self, tmp_path):
        """Test reading JSON with unicode characters."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"name": "日本語"}', encoding="utf-8")

        data = read_json(config_file)
        assert data["name"] == "日本語"


class TestExtractMcpServers:
    """Tests for MCP servers extraction."""

    def test_extract_camel_case(self):
        """Test extracting mcpServers (camelCase)."""
        data = {
            "mcpServers": {"server1": {"command": "test"}},
            "otherKey": "value",
        }
        result = extract_mcp_servers(data, McpKey.CAMEL)
        assert "server1" in result

    def test_extract_snake_case(self):
        """Test extracting mcp_servers (snake_case)."""
        data = {
            "mcp_servers": {"server1": {"command": "test"}},
            "other_key": "value",
        }
        result = extract_mcp_servers(data, McpKey.SNAKE)
        assert "server1" in result

    def test_extract_missing_key(self):
        """Test extracting when key is missing."""
        data = {"otherKey": "value"}
        result = extract_mcp_servers(data, McpKey.CAMEL)
        assert result is None

    def test_extract_nested_path(self):
        """Test extracting from nested location."""
        data = {"mcp": {"config": {"mcpServers": {"server1": {"command": "test"}}}}}
        result = extract_mcp_servers(data, McpKey.CAMEL, ["mcp", "config"])
        assert "server1" in result


class TestReadConfig:
    """Tests for full config reading."""

    def test_read_json_config(self, tmp_path):
        """Test reading a JSON config file."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "server1": {"command": "npx", "args": ["-y", "pkg"]},
                    },
                    "otherData": "preserved",
                }
            )
        )

        location = ConfigLocation(
            app_name="Test",
            path_template="",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        data, config = read_config(config_file, location)
        assert "otherData" in data
        assert config is not None
        assert len(config.servers) == 1

    def test_read_empty_mcp_servers(self, tmp_path):
        """Test reading config with empty mcpServers."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "mcpServers": {},
                }
            )
        )

        location = ConfigLocation(
            app_name="Test",
            path_template="",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        _, config = read_config(config_file, location)
        assert config is not None
        assert len(config.servers) == 0

    def test_read_no_mcp_servers(self, tmp_path):
        """Test reading config without mcpServers key."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "theme": "dark",
                }
            )
        )

        location = ConfigLocation(
            app_name="Test",
            path_template="",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        _, config = read_config(config_file, location)
        assert config is None
