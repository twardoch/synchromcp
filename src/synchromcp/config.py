"""Config file discovery and platform-specific paths."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileType(Enum):
    """Supported config file types."""

    JSON = "json"
    TOML = "toml"


class McpKey(Enum):
    """Key name for MCP servers section."""

    CAMEL = "mcpServers"  # JSON files
    SNAKE = "mcp_servers"  # TOML files


@dataclass
class ConfigLocation:
    """A known MCP config file location."""

    app_name: str
    path_template: str  # Uses {home}, {appdata}, {config} placeholders
    file_type: FileType
    mcp_key: McpKey
    nested_path: list[str] | None = (
        None  # For nested mcpServers (e.g., ["mcp", "servers"])
    )

    def expand_path(self, home: Path, mounts: list[Path] | None = None) -> list[Path]:
        """Expand path template to actual paths.

        Args:
            home: User's home directory
            mounts: Optional list of mount points to search

        Returns:
            List of expanded paths that exist
        """
        paths: list[Path] = []
        bases = [home]
        if mounts:
            bases.extend(mounts)

        for base in bases:
            expanded = self._expand_for_base(base, home)
            if expanded and expanded.exists():
                paths.append(expanded)

        return paths

    def _expand_for_base(self, base: Path, home: Path) -> Path | None:
        """Expand path for a specific base directory."""
        template = self.path_template

        # Platform-specific replacements
        system = platform.system()

        if system == "Darwin":  # macOS
            appdata = base / "Library" / "Application Support"
            config = base / ".config"
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", base / "AppData" / "Roaming"))
            if base != home:
                # For mounts, adjust appdata relative to base
                appdata = base / "AppData" / "Roaming"
            config = appdata
        else:  # Linux
            appdata = base / ".config"
            config = base / ".config"

        try:
            path_str = template.format(
                home=str(base),
                appdata=str(appdata),
                config=str(config),
            )
            return Path(path_str).expanduser()
        except KeyError:
            return None


# All known MCP config locations
KNOWN_LOCATIONS: list[ConfigLocation] = [
    # Claude Desktop
    ConfigLocation(
        app_name="Claude Desktop",
        path_template="{appdata}/Claude/claude_desktop_config.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Claude Code (user settings)
    ConfigLocation(
        app_name="Claude Code",
        path_template="{home}/.claude.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Cursor
    ConfigLocation(
        app_name="Cursor",
        path_template="{home}/.cursor/mcp.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # BoltAI
    ConfigLocation(
        app_name="BoltAI",
        path_template="{home}/.boltai/mcp.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Gemini CLI
    ConfigLocation(
        app_name="Gemini CLI",
        path_template="{home}/.gemini/settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Codex CLI (TOML)
    ConfigLocation(
        app_name="Codex CLI",
        path_template="{home}/.codex/config.toml",
        file_type=FileType.TOML,
        mcp_key=McpKey.SNAKE,
    ),
    # Jan
    ConfigLocation(
        app_name="Jan",
        path_template="{home}/jan/mcp_config.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Factory
    ConfigLocation(
        app_name="Factory",
        path_template="{home}/.factory/mcp.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Void Editor
    ConfigLocation(
        app_name="Void Editor",
        path_template="{home}/.void-editor/mcp.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # llxprt
    ConfigLocation(
        app_name="llxprt",
        path_template="{home}/.llxprt/settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Qwen
    ConfigLocation(
        app_name="Qwen",
        path_template="{home}/.qwen/settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Gemini Antigravity
    ConfigLocation(
        app_name="Gemini Antigravity",
        path_template="{home}/.gemini/antigravity/mcp_config.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # VSCode Kilo Code
    ConfigLocation(
        app_name="VSCode Kilo Code",
        path_template="{appdata}/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # VSCode Roo Code
    ConfigLocation(
        app_name="VSCode Roo Code",
        path_template="{appdata}/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # VSCode Insiders Kilo Code
    ConfigLocation(
        app_name="VSCode Insiders Kilo Code",
        path_template="{appdata}/Code - Insiders/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # VSCode Insiders Roo Code
    ConfigLocation(
        app_name="VSCode Insiders Roo Code",
        path_template="{appdata}/Code - Insiders/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Cursor Kilo Code
    ConfigLocation(
        app_name="Cursor Kilo Code",
        path_template="{appdata}/Cursor/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Cursor Roo Code
    ConfigLocation(
        app_name="Cursor Roo Code",
        path_template="{appdata}/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Antigravity Kilo Code
    ConfigLocation(
        app_name="Antigravity Kilo Code",
        path_template="{appdata}/Antigravity/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
    # Antigravity Roo Code
    ConfigLocation(
        app_name="Antigravity Roo Code",
        path_template="{appdata}/Antigravity/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json",
        file_type=FileType.JSON,
        mcp_key=McpKey.CAMEL,
    ),
]


@dataclass
class DiscoveredConfig:
    """A discovered config file with its metadata."""

    location: ConfigLocation
    path: Path


def discover_configs(
    mounts: list[str] | None = None,
) -> list[DiscoveredConfig]:
    """Discover all MCP config files on the system.

    Args:
        mounts: Optional list of mount points to search

    Returns:
        List of discovered config files
    """
    home = Path.home()
    mount_paths = [Path(m) for m in mounts] if mounts else None

    discovered: list[DiscoveredConfig] = []

    for location in KNOWN_LOCATIONS:
        paths = location.expand_path(home, mount_paths)
        for path in paths:
            discovered.append(DiscoveredConfig(location=location, path=path))

    return discovered


def get_default_source() -> Path | None:
    """Get the default source config file (Claude Desktop)."""
    home = Path.home()
    for location in KNOWN_LOCATIONS:
        if location.app_name == "Claude Desktop":
            paths = location.expand_path(home)
            if paths:
                return paths[0]
    return None
