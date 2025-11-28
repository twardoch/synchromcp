# synchromcp - MCP Settings Synchronization Tool

## Scope

A Python CLI tool that synchronizes MCP (Model Context Protocol) server configurations between different AI apps and across machines.

---

## 1. MCP Config File Locations

### 1.1 macOS

| App | Path |
|-----|------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Code (user) | `~/.claude.json` |
| Claude Code (project) | `./.mcp.json` |
| Cursor | `~/.cursor/mcp.json` |
| BoltAI | `~/.boltai/mcp.json` |
| Gemini CLI | `~/.gemini/settings.json` |
| Codex CLI | `~/.codex/config.toml` |
| Jan | `~/jan/mcp_config.json` |
| Factory | `~/.factory/mcp.json` |
| Void Editor | `~/.void-editor/mcp.json` |
| llxprt | `~/.llxprt/settings.json` |
| Qwen | `~/.qwen/settings.json` |
| Antigravity/Gemini | `~/.gemini/antigravity/mcp_config.json` |
| VSCode Kilo Code | `~/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json` |
| VSCode Roo Code | `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` |
| VSCode Insiders Kilo | `~/Library/Application Support/Code - Insiders/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json` |
| VSCode Insiders Roo | `~/Library/Application Support/Code - Insiders/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` |
| Cursor Kilo Code | `~/Library/Application Support/Cursor/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json` |
| Cursor Roo Code | `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` |
| Antigravity Kilo | `~/Library/Application Support/Antigravity/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json` |
| Antigravity Roo | `~/Library/Application Support/Antigravity/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` |

### 1.2 Windows

| App | Path |
|-----|------|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Code (user) | `%USERPROFILE%\.claude.json` |
| Cursor | `%USERPROFILE%\.cursor\mcp.json` |
| BoltAI | `%USERPROFILE%\.boltai\mcp.json` |
| Gemini CLI | `%USERPROFILE%\.gemini\settings.json` |
| Codex CLI | `%USERPROFILE%\.codex\config.toml` |
| Jan | `%USERPROFILE%\jan\mcp_config.json` |
| VSCode Kilo Code | `%APPDATA%\Code\User\globalStorage\kilocode.kilo-code\settings\mcp_settings.json` |
| VSCode Roo Code | `%APPDATA%\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\mcp_settings.json` |

### 1.3 Linux

| App | Path |
|-----|------|
| Claude Desktop | `~/.config/Claude/claude_desktop_config.json` |
| Claude Code (user) | `~/.claude.json` |
| Cursor | `~/.cursor/mcp.json` |
| Gemini CLI | `~/.gemini/settings.json` |
| Codex CLI | `~/.codex/config.toml` |
| VSCode Kilo Code | `~/.config/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json` |
| VSCode Roo Code | `~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` |

---

## 2. Unified mcpServers Schema

### 2.1 JSON Schema for mcpServers

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Servers Configuration",
  "type": "object",
  "additionalProperties": {
    "$ref": "#/definitions/McpServer"
  },
  "definitions": {
    "McpServer": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "description": "Executable command to run the MCP server (for stdio transport)"
        },
        "args": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Command-line arguments for the server"
        },
        "env": {
          "type": "object",
          "additionalProperties": { "type": "string" },
          "description": "Environment variables for the server process"
        },
        "cwd": {
          "type": "string",
          "description": "Working directory to launch the server from"
        },
        "url": {
          "type": "string",
          "format": "uri",
          "description": "URL for HTTP/SSE transport servers"
        },
        "type": {
          "type": "string",
          "enum": ["stdio", "sse", "streamable-http", "streamableHttp"],
          "description": "Transport type for the server"
        },
        "disabled": {
          "type": "boolean",
          "default": false,
          "description": "Whether the server is disabled"
        },
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Whether the server is enabled (alternative to disabled)"
        },
        "alwaysAllow": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of tools to auto-approve without prompting"
        },
        "timeout": {
          "type": "integer",
          "description": "Network timeout in seconds"
        },
        "trust": {
          "type": "boolean",
          "description": "Bypass confirmation dialogs (Gemini CLI)"
        },
        "bearerTokenEnvVar": {
          "type": "string",
          "description": "Environment variable containing bearer token (Codex)"
        },
        "httpHeaders": {
          "type": "object",
          "additionalProperties": { "type": "string" },
          "description": "HTTP headers for remote servers (Codex)"
        }
      },
      "oneOf": [
        { "required": ["command"] },
        { "required": ["url"] }
      ]
    }
  }
}
```

### 2.2 Field Mapping by App

| Field | Claude | Cursor | Cline/Roo | Kilo | Gemini | Codex | BoltAI |
|-------|--------|--------|-----------|------|--------|-------|--------|
| command | Y | Y | Y | Y | Y | Y | Y |
| args | Y | Y | Y | Y | Y | Y | Y |
| env | Y | Y | Y | Y | Y | Y | Y |
| cwd | - | - | - | - | - | Y | - |
| url | - | Y | Y | Y | Y | Y | - |
| type | - | Y | Y | Y | - | - | - |
| disabled | - | Y | Y | Y | - | - | - |
| alwaysAllow | - | - | Y | Y | - | - | - |
| trust | - | - | - | - | Y | - | - |
| bearerTokenEnvVar | - | - | - | - | - | Y | - |
| httpHeaders | - | - | - | - | - | Y | - |

---

## 3. Config File Structures

### 3.1 JSON Files - mcpServers at Root

Apps: Claude Desktop, Cursor, BoltAI, Jan

```json
{
  "mcpServers": { ... }
}
```

### 3.2 JSON Files - mcpServers Nested

Apps: Gemini CLI, llxprt, Qwen

```json
{
  "theme": "...",
  "selectedAuthType": "...",
  "mcpServers": { ... },
  "mcp": {
    "allowed": [],
    "excluded": []
  }
}
```

### 3.3 TOML Files

Apps: Codex CLI

```toml
[mcp_servers.server_name]
command = "npx"
args = ["-y", "@pkg/server"]

[mcp_servers.http_server]
url = "https://example.com/mcp"
```

---

## 4. Package Architecture

### 4.1 Project Structure

```
synchromcp/
├── src/
│   └── synchromcp/
│       ├── __init__.py
│       ├── __main__.py       # CLI entry point
│       ├── cli.py            # Fire CLI implementation
│       ├── config.py         # Config file discovery & locations
│       ├── models.py         # Pydantic models for mcpServers
│       ├── readers.py        # JSON/TOML file readers
│       ├── writers.py        # JSON/TOML file writers (preserving other data)
│       └── sync.py           # Sync logic
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_readers.py
│   ├── test_writers.py
│   └── test_sync.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── PLAN.md
├── TODO.md
└── CLAUDE.md
```

### 4.2 Dependencies

| Package | Purpose |
|---------|---------|
| fire | CLI framework |
| pydantic | Data validation and models |
| tomli | TOML reading (Python 3.11+ has tomllib) |
| tomli-w | TOML writing |
| rich | Pretty console output |
| loguru | Logging |

### 4.3 Key Design Decisions

1. **Preserve existing data**: When updating config files, only modify the `mcpServers` section. All other keys remain untouched.

2. **Platform detection**: Auto-detect OS and use appropriate paths. Support `--mounts` for external volumes.

3. **Parent source**: Default to Claude Desktop config as the source of truth. Override with `--source`.

4. **Validation**: Parse and validate mcpServers using Pydantic before syncing.

5. **Dry run**: Support `--dry-run` to preview changes without writing.

6. **TOML handling**: The TOML format uses `mcp_servers` (underscore) instead of `mcpServers` (camelCase). Convert appropriately.

---

## 5. CLI Interface

### 5.1 Commands

```bash
# List all discovered config files
synchromcp list

# Show mcpServers from a specific source
synchromcp show [--source PATH]

# Sync from source to all targets
synchromcp sync [--source PATH] [--targets PATH,...] [--mounts PATH,...] [--dry-run]

# Validate a config file
synchromcp validate PATH

# Export unified schema
synchromcp schema
```

### 5.2 Options

| Option | Description |
|--------|-------------|
| `--source` | Path to source config file (default: Claude Desktop) |
| `--targets` | Comma-separated list of target paths (default: all discovered) |
| `--mounts` | Comma-separated list of mount points for external volumes |
| `--dry-run` | Show what would change without writing |
| `--verbose` | Enable verbose output |
| `--format` | Output format: text, json, yaml |

---

## 6. Implementation Plan

### Phase 1: Core Infrastructure

1. Set up project with hatch and hatch-vcs
2. Define Pydantic models for mcpServers
3. Implement config file discovery
4. Implement JSON reader/writer (preserving other data)
5. Implement TOML reader/writer (preserving other data)

### Phase 2: CLI and Sync

1. Implement Fire CLI with list, show, validate commands
2. Implement sync command
3. Add --mounts support for external volumes
4. Add --dry-run support

### Phase 3: Testing and Polish

1. Write comprehensive tests
2. Add GitHub Actions for CI/CD
3. Add git-tag-based versioning
4. Write documentation

---

## 7. Sync Algorithm

```
1. Discover all config files on system and mounts
2. Read source config file
3. Extract and validate mcpServers section
4. For each target config file:
   a. Read existing content
   b. Parse to determine file type (JSON or TOML)
   c. Replace mcpServers/mcp_servers section with source data
   d. Preserve all other data
   e. Write back to file (or show diff if --dry-run)
5. Report summary of changes
```

---

## 8. Error Handling

1. **Missing source file**: Error with helpful message
2. **Invalid JSON/TOML**: Error with parse location
3. **Invalid mcpServers data**: Validation error with field details
4. **Permission denied**: Warning, skip file, continue
5. **Mount not found**: Warning, continue with available files

---

## 9. Future Considerations (Out of Scope)

- GUI interface
- Watch mode for auto-sync
- Cloud sync
- Encryption of sensitive values
- MCP server health checking
