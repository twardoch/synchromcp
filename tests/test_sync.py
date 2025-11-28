"""Tests for sync logic."""

import json
from pathlib import Path

import pytest

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
