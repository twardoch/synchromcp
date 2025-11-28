"""Sync logic for MCP configurations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from synchromcp.config import (
    ConfigLocation,
    DiscoveredConfig,
    FileType,
    McpKey,
    discover_configs,
    get_default_source,
)
from synchromcp.models import McpServersConfig
from synchromcp.readers import read_config
from synchromcp.writers import write_config


@dataclass
class SyncResult:
    """Result of a sync operation."""

    path: Path
    app_name: str
    success: bool
    message: str
    servers_count: int = 0


def load_source(source_path: Path | None = None) -> tuple[Path, McpServersConfig]:
    """Load MCP servers from source config.

    Args:
        source_path: Optional explicit source path. If None, uses default.

    Returns:
        Tuple of (source_path, config)

    Raises:
        FileNotFoundError: If source file doesn't exist
        ValueError: If source has no valid MCP servers
    """
    if source_path is None:
        source_path = get_default_source()
        if source_path is None:
            msg = "No default source found (Claude Desktop config)"
            raise FileNotFoundError(msg)

    if not source_path.exists():
        msg = f"Source file not found: {source_path}"
        raise FileNotFoundError(msg)

    # Determine file type from extension
    if source_path.suffix.lower() == ".toml":
        file_type = FileType.TOML
        mcp_key = McpKey.SNAKE
    else:
        file_type = FileType.JSON
        mcp_key = McpKey.CAMEL

    # Create a temporary location for reading
    temp_location = ConfigLocation(
        app_name="Source",
        path_template="",
        file_type=file_type,
        mcp_key=mcp_key,
    )

    _, config = read_config(source_path, temp_location)
    if config is None:
        msg = f"No valid MCP servers found in source: {source_path}"
        raise ValueError(msg)

    return source_path, config


def sync_configs(
    source_path: Path | None = None,
    target_paths: list[str] | None = None,
    mounts: list[str] | None = None,
    dry_run: bool = False,
) -> list[SyncResult]:
    """Sync MCP configurations from source to targets.

    Args:
        source_path: Path to source config. If None, uses Claude Desktop.
        target_paths: Optional list of specific target paths.
        mounts: Optional list of mount points for external volumes.
        dry_run: If True, don't write changes.

    Returns:
        List of sync results
    """
    results: list[SyncResult] = []

    # Load source
    try:
        source, config = load_source(source_path)
        logger.info(f"Loaded {len(config.servers)} servers from {source}")
    except (FileNotFoundError, ValueError) as e:
        return [
            SyncResult(
                path=source_path or Path("unknown"),
                app_name="Source",
                success=False,
                message=str(e),
            )
        ]

    # Discover targets
    if target_paths:
        # Use explicit targets
        discovered: list[DiscoveredConfig] = []
        for target_str in target_paths:
            target_path = Path(target_str)
            if target_path.exists():
                # Guess file type and key
                if target_path.suffix.lower() == ".toml":
                    file_type = FileType.TOML
                    mcp_key = McpKey.SNAKE
                else:
                    file_type = FileType.JSON
                    mcp_key = McpKey.CAMEL

                location = ConfigLocation(
                    app_name=target_path.name,
                    path_template="",
                    file_type=file_type,
                    mcp_key=mcp_key,
                )
                discovered.append(DiscoveredConfig(location=location, path=target_path))
            else:
                results.append(
                    SyncResult(
                        path=target_path,
                        app_name=target_path.name,
                        success=False,
                        message="File not found",
                    )
                )
    else:
        # Discover all targets
        discovered = discover_configs(mounts)

    # Filter out source from targets
    discovered = [t for t in discovered if t.path.resolve() != source.resolve()]

    # Sync to each target
    for target in discovered:
        try:
            # Read existing data
            data, _ = read_config(target.path, target.location)

            if dry_run:
                results.append(
                    SyncResult(
                        path=target.path,
                        app_name=target.location.app_name,
                        success=True,
                        message="Would update (dry run)",
                        servers_count=len(config.servers),
                    )
                )
            else:
                write_config(target.path, data, config, target.location)
                results.append(
                    SyncResult(
                        path=target.path,
                        app_name=target.location.app_name,
                        success=True,
                        message="Updated",
                        servers_count=len(config.servers),
                    )
                )
                logger.info(f"Updated {target.path}")

        except PermissionError:
            results.append(
                SyncResult(
                    path=target.path,
                    app_name=target.location.app_name,
                    success=False,
                    message="Permission denied",
                )
            )
            logger.warning(f"Permission denied: {target.path}")
        except Exception as e:
            results.append(
                SyncResult(
                    path=target.path,
                    app_name=target.location.app_name,
                    success=False,
                    message=str(e),
                )
            )
            logger.error(f"Error updating {target.path}: {e}")

    return results
