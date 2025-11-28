# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Initial implementation of `synchromcp` package
- CLI commands: `list`, `show`, `sync`, `validate`, `schema`
- Support for 20+ AI app MCP config locations on macOS, Windows, and Linux
- Pydantic models for MCP server validation
- JSON and TOML config file support
- `--mounts` option for syncing to external volumes
- `--dry-run` option for previewing changes
- Comprehensive test suite with 32 tests
- GitHub Actions CI/CD workflows
- Type hints and mypy strict mode
- Zensical-based documentation build from `src_docs` to `docs`
- `build.sh` script that builds the Python package and docs
- CI and release workflows updated to run the docs build
