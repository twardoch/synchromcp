"""Tests for CLI interface."""

from unittest.mock import MagicMock, patch

from synchromcp.cli import SynchroCLI


class TestSynchroCLI:
    """Tests for SynchroCLI class."""

    def test_list_without_mounts(self, tmp_path):
        """Test list command without mounts."""
        # Create mock configs with proper attributes
        from synchromcp.config import ConfigLocation, DiscoveredConfig, FileType, McpKey

        mock_configs = [
            DiscoveredConfig(
                location=ConfigLocation(
                    app_name="TestApp1",
                    path_template="test1.json",
                    file_type=FileType.JSON,
                    mcp_key=McpKey.CAMEL,
                ),
                path=tmp_path / "config1.json"
            )
        ]

        cli = SynchroCLI()

        with patch('synchromcp.cli.discover_configs', return_value=mock_configs), \
             patch('synchromcp.cli.get_default_source', return_value=None), \
             patch('synchromcp.cli.console.print') as mock_print:

            cli.list()

            # Verify console.print was called with a table and summary
            assert mock_print.call_count >= 1
            # First call should be the table
            table_call = mock_print.call_args_list[0][0][0]
            assert hasattr(table_call, 'title')  # Should be a Table object

    def test_show_valid_config(self, tmp_path):
        """Test show command with valid config."""
        config_file = tmp_path / "config.json"

        cli = SynchroCLI()

        with patch('synchromcp.cli.load_source') as mock_load_source, \
             patch('synchromcp.cli.console.print'):

            # Mock real server objects properly
            from synchromcp.models import McpServer, McpServersConfig
            mock_config = McpServersConfig(servers={
                "server1": McpServer(command="npx", args=["-y", "pkg"])
            })
            mock_load_source.return_value = (config_file, mock_config)

            cli.show(str(config_file))

            mock_load_source.assert_called_once_with(config_file)

    def test_sync_basic(self, tmp_path):
        """Test basic sync command."""
        source = tmp_path / "source.json"
        targets_str = "/tmp/target1.json,/tmp/target2.json"  # Comma-separated string

        cli = SynchroCLI()

        with patch('synchromcp.cli.sync_configs') as mock_sync, \
             patch('synchromcp.cli.console.print'):

            mock_sync.return_value = [
                MagicMock(success=True, message="Updated", servers_count=2)
            ]

            cli.sync(str(source), targets=targets_str)

            mock_sync.assert_called_once_with(
                source_path=source,
                target_paths=["/tmp/target1.json", "/tmp/target2.json"],
                dry_run=False
            )

    def test_sync_with_dry_run(self, tmp_path):
        """Test sync command with dry run."""
        source = tmp_path / "source.json"

        cli = SynchroCLI()

        with patch('synchromcp.cli.sync_configs') as mock_sync, \
             patch('synchromcp.cli.console.print'):

            mock_sync.return_value = [
                MagicMock(success=True, message="Would update (dry run)", servers_count=2)
            ]

            cli.sync(str(source), dry_run=True)

            mock_sync.assert_called_once_with(
                source_path=source,
                target_paths=None,
                dry_run=True
            )

    def test_validate_valid_file(self, tmp_path):
        """Test validate command with valid file."""
        config_file = tmp_path / "valid.json"

        cli = SynchroCLI()

        with patch('synchromcp.cli.read_config') as mock_read, \
             patch('synchromcp.cli.console.print'):

            from synchromcp.models import McpServer, McpServersConfig
            mock_config = McpServersConfig(servers={
                "server1": McpServer(command="test", args=["arg1"])
            })
            mock_read.return_value = (MagicMock(), mock_config)

            cli.validate(str(config_file))

            mock_read.assert_called_once()

    def test_validate_missing_servers(self, tmp_path):
        """Test validate command with missing mcpServers."""
        config_file = tmp_path / "no_servers.json"

        cli = SynchroCLI()

        with patch('synchromcp.cli.read_config') as mock_read, \
             patch('synchromcp.cli.console.print') as mock_print:

            mock_read.return_value = (MagicMock(), None)

            cli.validate(str(config_file))

            # Should report no servers
            mock_print.assert_called()

    def test_schema_output(self):
        """Test schema command outputs JSON schema."""
        cli = SynchroCLI()

        # Just test the method doesn't raise an exception
        cli.schema()

    def test_command_methods_exist(self):
        """Test that all expected CLI methods exist."""
        cli = SynchroCLI()

        # These should all be callable methods
        assert callable(cli.list)
        assert callable(cli.show)
        assert callable(cli.sync)
        assert callable(cli.validate)
        assert callable(cli.schema)

    def test_cli_class_instantiation(self):
        """Test that SynchroCLI can be instantiated."""
        cli = SynchroCLI()
        assert isinstance(cli, SynchroCLI)
