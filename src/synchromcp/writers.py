"""File writers for JSON and TOML config files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tomli_w

from synchromcp.config import ConfigLocation, FileType, McpKey
from synchromcp.models import McpServersConfig


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write data to a JSON file with pretty formatting."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_toml(path: Path, data: dict[str, Any]) -> None:
    """Write data to a TOML file."""
    with path.open("wb") as f:
        tomli_w.dump(data, f)


def update_mcp_servers(
    data: dict[str, Any],
    mcp_config: McpServersConfig,
    mcp_key: McpKey,
    nested_path: list[str] | None = None,
) -> dict[str, Any]:
    """Update the mcpServers section in config data, preserving other data.

    Args:
        data: The full config data
        mcp_config: The new MCP servers configuration
        mcp_key: The key name to use (mcpServers or mcp_servers)
        nested_path: Optional path to nested location

    Returns:
        Updated config data with new MCP servers
    """
    key = mcp_key.value
    result = data.copy()

    # Convert config to appropriate format
    if mcp_key == McpKey.SNAKE:
        new_servers = mcp_config.to_toml_dict()
    else:
        new_servers = mcp_config.to_dict()

    if nested_path:
        # Navigate to nested location and update
        current = result
        for segment in nested_path[:-1]:
            if segment not in current:
                current[segment] = {}
            current = current[segment]

        last_segment = nested_path[-1]
        if last_segment not in current:
            current[last_segment] = {}
        current[last_segment][key] = new_servers
    else:
        # Update at top level
        result[key] = new_servers

    return result


def write_config(
    path: Path,
    data: dict[str, Any],
    mcp_config: McpServersConfig,
    location: ConfigLocation,
) -> None:
    """Write config to file, updating only the MCP servers section.

    Args:
        path: Path to the config file
        data: The full config data (to preserve other sections)
        mcp_config: The new MCP servers configuration
        location: ConfigLocation with file type and key info
    """
    updated = update_mcp_servers(
        data,
        mcp_config,
        location.mcp_key,
        location.nested_path,
    )

    if location.file_type == FileType.JSON:
        write_json(path, updated)
    else:
        write_toml(path, updated)
