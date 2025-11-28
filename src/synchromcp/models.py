"""Pydantic models for MCP server configurations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class McpServer(BaseModel):
    """Model for a single MCP server configuration.

    Supports both stdio (command-based) and HTTP (url-based) transports.
    """

    model_config = ConfigDict(extra="allow")

    # Stdio transport fields
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    cwd: str | None = None

    # HTTP transport fields
    url: str | None = None

    # Common fields
    type: str | None = None  # stdio, sse, streamable-http, streamableHttp
    disabled: bool | None = None
    enabled: bool | None = None
    alwaysAllow: list[str] | None = None
    timeout: int | None = None

    # Gemini CLI specific
    trust: bool | None = None

    # Codex CLI specific
    bearerTokenEnvVar: str | None = None
    httpHeaders: dict[str, str] | None = None

    @model_validator(mode="after")
    def validate_transport(self) -> McpServer:
        """Ensure either command or url is provided."""
        if not self.command and not self.url:
            msg = "Either 'command' or 'url' must be provided"
            raise ValueError(msg)
        return self

    @field_validator("args", mode="before")
    @classmethod
    def ensure_args_list(cls, v: Any) -> list[str] | None:
        """Ensure args is a list of strings."""
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        return list(v)

    def is_disabled(self) -> bool:
        """Check if server is disabled (handles both disabled and enabled fields)."""
        if self.disabled is not None:
            return self.disabled
        if self.enabled is not None:
            return not self.enabled
        return False

    def to_toml_dict(self) -> dict[str, Any]:
        """Convert to TOML-compatible dict (snake_case keys, no None values)."""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            # Convert camelCase to snake_case for TOML
            snake_key = "".join(
                f"_{c.lower()}" if c.isupper() else c for c in key
            ).lstrip("_")
            result[snake_key] = value
        return result


class McpServersConfig(BaseModel):
    """Container for multiple MCP server configurations."""

    model_config = ConfigDict(extra="forbid")

    servers: dict[str, McpServer]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> McpServersConfig:
        """Create from a raw dictionary of server configs."""
        servers = {
            name: McpServer.model_validate(config) for name, config in data.items()
        }
        return cls(servers=servers)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Convert to raw dictionary for JSON serialization."""
        return {
            name: server.model_dump(exclude_none=True)
            for name, server in self.servers.items()
        }

    def to_toml_dict(self) -> dict[str, dict[str, Any]]:
        """Convert to TOML-compatible dictionary."""
        return {name: server.to_toml_dict() for name, server in self.servers.items()}
