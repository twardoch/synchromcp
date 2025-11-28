"""Tests for file writers."""

import json

from synchromcp.config import ConfigLocation, FileType, McpKey
from synchromcp.models import McpServersConfig
from synchromcp.writers import update_mcp_servers, write_config, write_json


class TestWriteJson:
    """Tests for JSON writing."""

    def test_write_json(self, tmp_path):
        """Test writing JSON file."""
        config_file = tmp_path / "config.json"
        data = {"key": "value", "number": 42}

        write_json(config_file, data)

        content = config_file.read_text()
        assert '"key": "value"' in content
        assert content.endswith("\n")

    def test_write_json_unicode(self, tmp_path):
        """Test writing JSON with unicode."""
        config_file = tmp_path / "config.json"
        data = {"name": "日本語"}

        write_json(config_file, data)

        content = config_file.read_text(encoding="utf-8")
        assert "日本語" in content


class TestUpdateMcpServers:
    """Tests for updating MCP servers section."""

    def test_update_preserves_other_data(self):
        """Test that other data is preserved when updating."""
        data = {
            "theme": "dark",
            "mcpServers": {"old": {"command": "old"}},
            "settings": {"key": "value"},
        }
        config = McpServersConfig.from_dict(
            {
                "new": {"command": "new"},
            }
        )

        result = update_mcp_servers(data, config, McpKey.CAMEL)

        assert result["theme"] == "dark"
        assert result["settings"]["key"] == "value"
        assert "new" in result["mcpServers"]
        assert "old" not in result["mcpServers"]

    def test_update_adds_key_if_missing(self):
        """Test that mcpServers key is added if missing."""
        data = {"theme": "dark"}
        config = McpServersConfig.from_dict(
            {
                "server1": {"command": "test"},
            }
        )

        result = update_mcp_servers(data, config, McpKey.CAMEL)

        assert "mcpServers" in result
        assert "server1" in result["mcpServers"]


class TestWriteConfig:
    """Tests for full config writing."""

    def test_write_json_config(self, tmp_path):
        """Test writing JSON config file."""
        config_file = tmp_path / "config.json"
        original_data = {
            "theme": "dark",
            "mcpServers": {},
        }
        config = McpServersConfig.from_dict(
            {
                "server1": {"command": "npx", "args": ["-y", "pkg"]},
            }
        )
        location = ConfigLocation(
            app_name="Test",
            path_template="",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        write_config(config_file, original_data, config, location)

        written = json.loads(config_file.read_text())
        assert written["theme"] == "dark"
        assert "server1" in written["mcpServers"]
        assert written["mcpServers"]["server1"]["command"] == "npx"
