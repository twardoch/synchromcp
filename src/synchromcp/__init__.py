"""synchromcp - Synchronize MCP server configurations across AI apps and machines."""

try:
    from synchromcp._version import __version__
except ImportError:
    __version__ = "0.0.0"

from synchromcp.config import ConfigLocation, discover_configs
from synchromcp.models import McpServer, McpServersConfig
from synchromcp.sync import sync_configs

__all__ = [
    "ConfigLocation",
    "McpServer",
    "McpServersConfig",
    "__version__",
    "discover_configs",
    "sync_configs",
]
