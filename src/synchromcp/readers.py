"""File readers for JSON and TOML config files."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from synchromcp.config import ConfigLocation, FileType, McpKey
from synchromcp.models import McpServersConfig


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file and return its contents."""
    with path.open("r", encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML file and return its contents."""
    with path.open("rb") as f:
        return tomllib.load(f)


def extract_mcp_servers(
    data: dict[str, Any],
    mcp_key: McpKey,
    nested_path: list[str] | None = None,
) -> dict[str, Any] | None:
    """Extract the mcpServers/mcp_servers section from config data.

    Args:
        data: The full config data
        mcp_key: The key name to look for (mcpServers or mcp_servers)
        nested_path: Optional path to nested location

    Returns:
        The MCP servers dict, or None if key not found
    """
    key = mcp_key.value

    if nested_path:
        # Navigate to nested location
        current = data
        for segment in nested_path:
            if isinstance(current, dict) and segment in current:
                current = current[segment]
            else:
                return None
        if isinstance(current, dict) and key in current:
            result: dict[str, Any] = current[key]
            return result
        return None

    # Look for key at top level
    if key in data:
        result = data[key]
        return result
    return None


def read_config(
    path: Path,
    location: ConfigLocation,
) -> tuple[dict[str, Any], McpServersConfig | None]:
    """Read a config file and extract MCP servers.

    Args:
        path: Path to the config file
        location: ConfigLocation with file type and key info

    Returns:
        Tuple of (full_data, parsed_mcp_servers or None if invalid/empty)
    """
    if location.file_type == FileType.JSON:
        data = read_json(path)
    else:
        data = read_toml(path)

    mcp_data = extract_mcp_servers(data, location.mcp_key, location.nested_path)

    if mcp_data is None:
        return data, None

    try:
        config = McpServersConfig.from_dict(mcp_data)
        return data, config
    except Exception:
        # Invalid config, return None
        return data, None
