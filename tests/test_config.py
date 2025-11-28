"""Tests for config discovery."""

from pathlib import Path

from synchromcp.config import (
    ConfigLocation,
    FileType,
    McpKey,
    discover_configs,
)


class TestConfigLocation:
    """Tests for ConfigLocation."""

    def test_expand_home_path(self, tmp_path):
        """Test expanding home directory paths."""
        # Create a test config file
        config_file = tmp_path / ".cursor" / "mcp.json"
        config_file.parent.mkdir(parents=True)
        config_file.write_text('{"mcpServers": {}}')

        location = ConfigLocation(
            app_name="Test",
            path_template="{home}/.cursor/mcp.json",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        paths = location.expand_path(tmp_path)
        assert len(paths) == 1
        assert paths[0] == config_file

    def test_expand_with_mounts(self, tmp_path):
        """Test expanding paths with mount points."""
        # Create config in main home
        home_config = tmp_path / "home" / ".cursor" / "mcp.json"
        home_config.parent.mkdir(parents=True)
        home_config.write_text('{"mcpServers": {}}')

        # Create config in mount
        mount_config = tmp_path / "mount" / ".cursor" / "mcp.json"
        mount_config.parent.mkdir(parents=True)
        mount_config.write_text('{"mcpServers": {}}')

        location = ConfigLocation(
            app_name="Test",
            path_template="{home}/.cursor/mcp.json",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        paths = location.expand_path(
            tmp_path / "home",
            mounts=[tmp_path / "mount"],
        )
        assert len(paths) == 2

    def test_nonexistent_path_ignored(self, tmp_path):
        """Test that non-existent paths are not returned."""
        location = ConfigLocation(
            app_name="Test",
            path_template="{home}/.nonexistent/config.json",
            file_type=FileType.JSON,
            mcp_key=McpKey.CAMEL,
        )

        paths = location.expand_path(tmp_path)
        assert len(paths) == 0


class TestDiscoverConfigs:
    """Tests for config discovery."""

    def test_discover_with_no_configs(self, tmp_path, monkeypatch):
        """Test discovery when no configs exist."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        # No configs created, should find none
        _configs = discover_configs()
        # May find some if user has real configs, but in temp dir should be empty
        # This is more of a smoke test (just check it doesn't raise)

    def test_discover_with_mounts(self, tmp_path):
        """Test discovery with mount points."""
        mount1 = tmp_path / "mount1"
        mount2 = tmp_path / "mount2"

        # Create config in mount1
        config1 = mount1 / ".cursor" / "mcp.json"
        config1.parent.mkdir(parents=True)
        config1.write_text('{"mcpServers": {}}')

        configs = discover_configs(mounts=[str(mount1), str(mount2)])
        # Should find at least the one we created
        cursor_configs = [c for c in configs if c.location.app_name == "Cursor"]
        assert any(c.path == config1 for c in cursor_configs)
