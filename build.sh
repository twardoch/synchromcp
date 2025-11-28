#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required to build synchromcp. See CLAUDE.md for setup instructions." >&2
  exit 1
fi

echo "Syncing dependencies (including dev and docs extras)..."
uv sync --all-extras

echo "Building Python package with uv..."
uv build

echo "Building documentation with Zensical..."
uv run zensical build --clean

echo "Build complete."
echo "  - Python distributions: dist/"
echo "  - Documentation:       docs/"

