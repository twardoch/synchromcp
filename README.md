# synchromcp

Synchronize MCP (Model Context Protocol) server configurations across AI apps and machines.

## Problem

AI coding assistants store MCP server configs in different locations:
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Cursor: `~/.cursor/mcp.json`
- VSCode extensions: scattered across `globalStorage` directories
- Codex CLI: `~/.codex/config.toml` (different format!)

Keeping these in sync manually is tedious and error-prone.

## Solution

```bash
# Sync MCP servers from Claude Desktop to all other apps
synchromcp sync

# Preview changes without writing
synchromcp sync --dry-run

# Sync to external machine mounted at /Volumes/backup
synchromcp sync --mounts /Volumes/backup
```

## Installation

```bash
pip install synchromcp
```

Or with uv:

```bash
uv tool install synchromcp
```

## Usage

### List discovered config files

```bash
synchromcp list
```

Output:
```
Found 8 MCP config files:
  [source] ~/Library/Application Support/Claude/claude_desktop_config.json
  ~/.cursor/mcp.json
  ~/.boltai/mcp.json
  ~/.codex/config.toml
  ...
```

### Show current MCP servers

```bash
synchromcp show
```

Output:
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "~/Data"]
  },
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

### Sync to all targets

```bash
# Dry run first
synchromcp sync --dry-run

# Apply changes
synchromcp sync
```

### Sync to external volumes

```bash
synchromcp sync --mounts /Volumes/MacMini,/Volumes/Laptop
```

This syncs to config files on mounted external drives, useful for keeping multiple machines in sync.

### Use a different source

```bash
synchromcp sync --source ~/.cursor/mcp.json
```

### Validate a config file

```bash
synchromcp validate ~/.boltai/mcp.json
```

## Supported Apps

| App | macOS | Windows | Linux |
|-----|-------|---------|-------|
| Claude Desktop | Y | Y | Y |
| Claude Code | Y | Y | Y |
| Cursor | Y | Y | Y |
| BoltAI | Y | - | - |
| Gemini CLI | Y | Y | Y |
| Codex CLI | Y | Y | Y |
| Jan | Y | Y | Y |
| VSCode Kilo Code | Y | Y | Y |
| VSCode Roo Code | Y | Y | Y |

## How It Works

1. Discovers all MCP config files on your system
2. Reads the source config (default: Claude Desktop)
3. Validates the `mcpServers` section
4. Updates only the `mcpServers` section in each target file
5. Preserves all other data in target files

### JSON vs TOML

Most apps use JSON with a `mcpServers` key:

```json
{
  "mcpServers": {
    "server-name": { "command": "...", "args": [...] }
  }
}
```

Codex CLI uses TOML with a `mcp_servers` key:

```toml
[mcp_servers.server-name]
command = "..."
args = [...]
```

synchromcp handles the conversion automatically.

## Development

```bash
git clone https://github.com/twardoch/synchromcp.git
cd synchromcp
uv venv && uv pip install -e ".[dev]"
pytest
```

## License

MIT
