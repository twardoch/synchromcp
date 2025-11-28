"""CLI interface using Fire."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import fire  # type: ignore[import-untyped]
from loguru import logger
from rich.console import Console
from rich.table import Table

from synchromcp.config import discover_configs, get_default_source
from synchromcp.readers import read_config
from synchromcp.sync import load_source, sync_configs

# Configure loguru
logger.remove()
logger.add(sys.stderr, format="{message}", level="INFO")

console = Console()


class SynchroCLI:
    """Synchronize MCP server configurations across AI apps and machines."""

    def list(self, mounts: str | None = None) -> None:
        """List all discovered MCP config files.

        Args:
            mounts: Comma-separated list of mount points to search
        """
        mount_list = mounts.split(",") if mounts else None
        configs = discover_configs(mount_list)
        default_source = get_default_source()

        table = Table(title="Discovered MCP Config Files")
        table.add_column("App", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")

        for config in configs:
            is_source = (
                default_source and config.path.resolve() == default_source.resolve()
            )
            status = "[source]" if is_source else ""

            table.add_row(
                config.location.app_name,
                str(config.path),
                config.location.file_type.value,
                status,
            )

        if configs:
            console.print(table)
            console.print(f"\nFound {len(configs)} config file(s)")
        else:
            console.print("[yellow]No MCP config files found[/yellow]")

    def show(self, source: str | None = None) -> None:
        """Show MCP servers from a config file.

        Args:
            source: Path to config file (default: Claude Desktop)
        """
        try:
            source_path = Path(source) if source else None
            path, config = load_source(source_path)

            console.print(f"[cyan]Source:[/cyan] {path}\n")

            # Pretty print the config
            output = json.dumps(config.to_dict(), indent=2)
            console.print(output)

            console.print(f"\n[green]{len(config.servers)} server(s)[/green]")

        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)

    def sync(
        self,
        source: str | None = None,
        targets: str | None = None,
        mounts: str | None = None,
        dry_run: bool = False,
    ) -> None:
        """Sync MCP configurations from source to all targets.

        Args:
            source: Path to source config (default: Claude Desktop)
            targets: Comma-separated list of target paths (default: all discovered)
            mounts: Comma-separated list of mount points for external volumes
            dry_run: Show what would change without writing
        """
        source_path = Path(source) if source else None
        target_list = targets.split(",") if targets else None
        mount_list = mounts.split(",") if mounts else None

        if dry_run:
            console.print("[yellow]Dry run mode - no changes will be made[/yellow]\n")

        results = sync_configs(
            source_path=source_path,
            target_paths=target_list,
            mounts=mount_list,
            dry_run=dry_run,
        )

        table = Table(title="Sync Results")
        table.add_column("App", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Message", style="white")

        success_count = 0
        fail_count = 0

        for result in results:
            if result.success:
                status = "[green]OK[/green]"
                success_count += 1
            else:
                status = "[red]FAIL[/red]"
                fail_count += 1

            table.add_row(
                result.app_name,
                str(result.path),
                status,
                result.message,
            )

        console.print(table)
        console.print(
            f"\n[green]{success_count} succeeded[/green], [red]{fail_count} failed[/red]"
        )

    def validate(self, path: str) -> None:
        """Validate a config file.

        Args:
            path: Path to config file to validate
        """
        from synchromcp.config import ConfigLocation, FileType, McpKey

        config_path = Path(path)
        if not config_path.exists():
            console.print(f"[red]File not found:[/red] {path}")
            sys.exit(1)

        # Guess file type
        if config_path.suffix.lower() == ".toml":
            file_type = FileType.TOML
            mcp_key = McpKey.SNAKE
        else:
            file_type = FileType.JSON
            mcp_key = McpKey.CAMEL

        location = ConfigLocation(
            app_name="Validation",
            path_template="",
            file_type=file_type,
            mcp_key=mcp_key,
        )

        try:
            _, config = read_config(config_path, location)

            if config is None:
                console.print(f"[yellow]No MCP servers found in {path}[/yellow]")
            else:
                console.print(
                    f"[green]Valid config with {len(config.servers)} server(s)[/green]"
                )

                for name, server in config.servers.items():
                    transport = "url" if server.url else "command"
                    status = (
                        "[red]disabled[/red]"
                        if server.is_disabled()
                        else "[green]enabled[/green]"
                    )
                    console.print(f"  - {name}: {transport} {status}")

        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Validation error:[/red] {e}")
            sys.exit(1)

    def schema(self) -> None:
        """Output the JSON schema for mcpServers."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MCP Servers Configuration",
            "type": "object",
            "additionalProperties": {"$ref": "#/definitions/McpServer"},
            "definitions": {
                "McpServer": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Executable command (stdio transport)",
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command arguments",
                        },
                        "env": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                            "description": "Environment variables",
                        },
                        "cwd": {"type": "string", "description": "Working directory"},
                        "url": {
                            "type": "string",
                            "format": "uri",
                            "description": "URL (HTTP transport)",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["stdio", "sse", "streamable-http"],
                            "description": "Transport type",
                        },
                        "disabled": {
                            "type": "boolean",
                            "description": "Whether server is disabled",
                        },
                        "alwaysAllow": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Auto-approved tools",
                        },
                    },
                    "oneOf": [{"required": ["command"]}, {"required": ["url"]}],
                }
            },
        }
        print(json.dumps(schema, indent=2))


def main() -> None:
    """Entry point for the CLI."""
    fire.Fire(SynchroCLI)


if __name__ == "__main__":
    main()
