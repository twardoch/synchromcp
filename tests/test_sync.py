"""Tests for sync logic."""

import json
from unittest.mock import patch

import pytest

from synchromcp.config import (
    ConfigLocation,
    DiscoveredConfig,
    FileType,
    McpKey,
)
from synchromcp.sync import load_source, sync_configs


class TestLoadSource:
    """Tests for load_source function."""

    def test_load_valid_source(self, tmp_path):
        """Test loading a valid source config."""
        source_file = tmp_path / "source.json"
        source_file.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "npx", "args": ["-y", "pkg"]},
            }
        }))

        path, config = load_source(source_file)
        assert path == source_file
        assert len(config.servers) == 1
        assert "server1" in config.servers

    def test_load_missing_source(self, tmp_path):
        """Test loading a non-existent source file."""
        source_file = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError):
            load_source(source_file)

    def test_load_source_no_mcp_servers(self, tmp_path):
        """Test loading a source without mcpServers key."""
        source_file = tmp_path / "source.json"
        source_file.write_text(json.dumps({"theme": "dark"}))

        with pytest.raises(ValueError, match="No valid MCP servers"):
            load_source(source_file)


class TestSyncConfigs:
    """Tests for sync_configs function."""

    def test_sync_to_single_target(self, tmp_path):
        """Test syncing to a single target file."""
        # Create source
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "new_server": {"command": "npx", "args": ["-y", "new"]},
            }
        }))

        # Create target with existing data
        target = tmp_path / "target.json"
        target.write_text(json.dumps({
            "theme": "dark",
            "mcpServers": {
                "old_server": {"command": "old"},
            }
        }))

        results = sync_configs(
            source_path=source,
            target_paths=[str(target)],
        )

        assert len(results) == 1
        assert results[0].success is True

        # Verify target was updated
        written = json.loads(target.read_text())
        assert "new_server" in written["mcpServers"]
        assert "old_server" not in written["mcpServers"]
        assert written["theme"] == "dark"  # Other data preserved

    def test_sync_dry_run(self, tmp_path):
        """Test sync with dry-run mode."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test"},
            }
        }))

        target = tmp_path / "target.json"
        original_content = json.dumps({
            "mcpServers": {
                "old": {"command": "old"},
            }
        })
        target.write_text(original_content)

        results = sync_configs(
            source_path=source,
            target_paths=[str(target)],
            dry_run=True,
        )

        assert len(results) == 1
        assert results[0].success is True
        assert "dry run" in results[0].message.lower()

        # Verify target was NOT changed
        assert target.read_text() == original_content

    def test_sync_missing_target(self, tmp_path):
        """Test sync when target file doesn't exist."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test"},
            }
        }))

        results = sync_configs(
            source_path=source,
            target_paths=[str(tmp_path / "missing.json")],
        )

        assert len(results) == 1
        assert results[0].success is False
        assert "not found" in results[0].message.lower()

    def test_sync_multiple_targets(self, tmp_path):
        """Test syncing to multiple target files."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test"},
            }
        }))

        targets = []
        for i in range(3):
            target = tmp_path / f"target{i}.json"
            target.write_text(json.dumps({"mcpServers": {}}))
            targets.append(str(target))

        results = sync_configs(
            source_path=source,
            target_paths=targets,
        )

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_sync_source_excluded_from_targets(self, tmp_path):
        """Test that source file is excluded from targets."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test"},
            }
        }))

        # Try to sync to source itself
        results = sync_configs(
            source_path=source,
            target_paths=[str(source)],
        )

        # Source should be filtered out
        assert len(results) == 0

    def test_sync_toml_source(self, tmp_path):
        """Test syncing from a TOML source file."""
        source = tmp_path / "source.toml"
        source.write_text("""
[mcp_servers.server1]
command = "npx"
args = ["-y", "pkg"]

[mcp_servers.server2]
command = "python"
args = ["server.py"]
""")

        target = tmp_path / "target.json"
        target.write_text(json.dumps({"mcpServers": {}}))

        results = sync_configs(
            source_path=source,
            target_paths=[str(target)],
        )

        assert len(results) == 1
        assert results[0].success is True

        # Verify target was updated
        written = json.loads(target.read_text())
        assert "server1" in written["mcpServers"]
        assert "server2" in written["mcpServers"]

    def test_sync_toml_target(self, tmp_path):
        """Test syncing to a TOML target file."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test", "args": ["arg1"]},
            }
        }))

        target = tmp_path / "target.toml"
        target.write_text("""
[mcp_servers.old_server]
command = "old"
""")

        results = sync_configs(
            source_path=source,
            target_paths=[str(target)],
        )

        assert len(results) == 1
        assert results[0].success is True

        # Verify target was updated and old data preserved
        import tomllib
        written = tomllib.loads(target.read_text())
        assert "server1" in written["mcp_servers"]
        assert "old_server" not in written["mcp_servers"]

    def test_sync_with_discovery(self, tmp_path, monkeypatch):
        """Test sync with automatic target discovery."""
        # Create source
        source = tmp_path / "source.json"
        source.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "test"},
            }
        }))

        # Mock discover_configs to return some test configs
        mock_discovered = [
            DiscoveredConfig(
                location=ConfigLocation(
                    app_name="TestApp",
                    path_template="test.json",
                    file_type=FileType.JSON,
                    mcp_key=McpKey.CAMEL,
                ),
                path=tmp_path / "test1.json"
            ),
            DiscoveredConfig(
                location=ConfigLocation(
                    app_name="TestApp2",
                    path_template="test2.json",
                    file_type=FileType.JSON,
                    mcp_key=McpKey.CAMEL,
                ),
                path=tmp_path / "test2.json"
            )
        ]

        # Create test config files
        for discovered in mock_discovered:
            discovered.path.write_text(json.dumps({"mcpServers": {}}))

        with patch('synchromcp.sync.discover_configs', return_value=mock_discovered):
            results = sync_configs(source_path=source)

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_sync_source_load_error_propagation(self, tmp_path):
        """Test that source load errors are properly captured in results."""
        source = tmp_path / "nonexistent.json"

        results = sync_configs(source_path=source)

        assert len(results) == 1
        assert results[0].success is False
        assert "not found" in results[0].message.lower()

    def test_sync_with_empty_server_list(self, tmp_path):
        """Test syncing with empty server configuration."""
        source = tmp_path / "source.json"
        source.write_text(json.dumps({"mcpServers": {}}))

        target = tmp_path / "target.json"
        target.write_text(json.dumps({
            "mcpServers": {
                "old": {"command": "old"},
            }
        }))

        results = sync_configs(
            source_path=source,
            target_paths=[str(target)],
        )

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].servers_count == 0

        # Verify target was cleared
        written = json.loads(target.read_text())
        assert written["mcpServers"] == {}


class TestLoadSource:
    """Tests for load_source function."""

    def test_load_valid_source(self, tmp_path):
        """Test loading a valid source config."""
        source_file = tmp_path / "source.json"
        source_file.write_text(json.dumps({
            "mcpServers": {
                "server1": {"command": "npx", "args": ["-y", "pkg"]},
            }
        }))

        path, config = load_source(source_file)
        assert path == source_file
        assert len(config.servers) == 1
        assert "server1" in config.servers

    def test_load_toml_source(self, tmp_path):
        """Test loading a TOML source config."""
        source_file = tmp_path / "source.toml"
        source_file.write_text("""
[mcp_servers.test_server]
command = "python"
args = ["server.py"]
[mcp_servers.test_server.env]
TEST = "value"
""")

        path, config = load_source(source_file)
        assert path == source_file
        assert len(config.servers) == 1
        assert "test_server" in config.servers
        assert config.servers["test_server"].command == "python"

    def test_load_missing_source(self, tmp_path):
        """Test loading a non-existent source file."""
        source_file = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError):
            load_source(source_file)

    def test_load_source_no_mcp_servers(self, tmp_path):
        """Test loading a source without mcpServers key."""
        source_file = tmp_path / "source.json"
        source_file.write_text(json.dumps({"theme": "dark"}))

        with pytest.raises(ValueError, match="No valid MCP servers"):
            load_source(source_file)

    def test_load_source_with_invalid_data(self, tmp_path):
        """Test loading source with invalid MCP server data."""
        source_file = tmp_path / "source.json"
        source_file.write_text(json.dumps({
            "mcpServers": {
                "invalid_server": {
                    # Missing both command and url - should fail validation
                    "environment": {"TEST": "value"}
                }
            }
        }))

        with pytest.raises(ValueError, match="No valid MCP servers"):
            load_source(source_file)

    @patch('synchromcp.sync.get_default_source')
    def test_load_source_uses_default_when_none(self, mock_get_default, tmp_path):
        """Test that load_source uses get_default_source when source_path is None."""
        default_file = tmp_path / "default.json"
        default_file.write_text(json.dumps({
            "mcpServers": {
                "default": {"command": "default"},
            }
        }))
        mock_get_default.return_value = default_file

        path, config = load_source(None)
        assert path == default_file
        assert "default" in config.servers

    @patch('synchromcp.sync.get_default_source')
    def test_load_source_no_default_available(self, mock_get_default):
        """Test load_source when no default source is available."""
        mock_get_default.return_value = None

        with pytest.raises(FileNotFoundError, match="No default source found"):
            load_source(None)
