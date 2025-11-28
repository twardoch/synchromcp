# TODO - synchromcp

## Phase 1: Project Setup

- [x] Initialize project with `uv init`
- [x] Configure `pyproject.toml` with hatch and hatch-vcs
- [x] Add dependencies: fire, pydantic, tomli, tomli-w, rich, loguru
- [x] Add dev dependencies: pytest, pytest-cov, ruff, mypy
- [x] Create GitHub Actions workflow for CI/CD
- [x] Create GitHub Actions workflow for git-tag-based releases

## Phase 2: Core Models

- [x] Create `models.py` with Pydantic models
- [x] Define `McpServer` model with all fields
- [x] Define `McpServersConfig` model for the dict wrapper
- [x] Add validation for command vs url requirement
- [x] Add field normalization (disabled/enabled, type variants)
- [x] Write tests for models

## Phase 3: Config Discovery

- [x] Create `config.py` with config file locations
- [x] Define `ConfigLocation` dataclass with app name, path template, file type
- [x] Implement platform detection (macOS, Windows, Linux)
- [x] Implement path expansion with `~` and env vars
- [x] Implement config file discovery function
- [x] Support `--mounts` for external volume paths
- [x] Write tests for config discovery

## Phase 4: Readers

- [x] Create `readers.py` with file readers
- [x] Implement JSON reader that extracts mcpServers
- [x] Implement TOML reader that extracts mcp_servers
- [x] Handle nested mcpServers (Gemini settings.json)
- [x] Handle missing or empty mcpServers gracefully
- [x] Validate extracted data against Pydantic models
- [x] Write tests for readers

## Phase 5: Writers

- [x] Create `writers.py` with file writers
- [x] Implement JSON writer that preserves other data
- [x] Implement TOML writer that preserves other data
- [x] Handle mcpServers -> mcp_servers key conversion for TOML
- [ ] Create backup before writing (optional)
- [x] Write tests for writers

## Phase 6: Sync Logic

- [x] Create `sync.py` with sync functions
- [x] Implement source reading and validation
- [x] Implement target discovery
- [x] Implement sync algorithm
- [x] Support dry-run mode (diff output)
- [x] Report summary of changes
- [ ] Write tests for sync logic

## Phase 7: CLI

- [x] Create `cli.py` with Fire CLI
- [x] Implement `list` command - show discovered configs
- [x] Implement `show` command - display mcpServers from source
- [x] Implement `sync` command - sync from source to targets
- [x] Implement `validate` command - validate a config file
- [x] Implement `schema` command - output JSON schema
- [x] Add `--source`, `--targets`, `--mounts`, `--dry-run`, `--verbose` options
- [x] Add rich output formatting
- [x] Create `__main__.py` entry point
- [ ] Write tests for CLI

## Phase 8: Documentation

- [x] Write README.md with usage examples
- [x] Write CHANGELOG.md
- [x] Update CLAUDE.md with project-specific notes
- [x] Add basic Zensical docs build from `src_docs` to `docs`
- [x] Add docstrings to all public functions
- [x] Add type hints to all functions

## Phase 9: Testing & Quality

- [ ] Achieve 80%+ test coverage
- [x] Run ruff check and format
- [x] Run mypy type checking
- [x] Test on macOS
- [ ] Test on Windows (if available)
- [ ] Test on Linux (if available)
- [ ] Test with external mount paths

## Phase 10: Release

- [ ] Tag initial release v0.1.0
- [ ] Verify GitHub Actions release workflow
- [ ] Publish to PyPI
- [ ] Update README with PyPI badge
