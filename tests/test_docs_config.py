from __future__ import annotations

from pathlib import Path
import tomllib


def test_zensical_config_uses_src_docs_and_docs() -> None:
    """Ensure Zensical is configured to build from src_docs to docs."""
    config_path = Path(__file__).parents[1] / "zensical.toml"
    content = config_path.read_text(encoding="utf-8")
    data = tomllib.loads(content)
    project = data.get("project", {})

    assert project.get("docs_dir") == "src_docs"
    assert project.get("site_dir") == "docs"

