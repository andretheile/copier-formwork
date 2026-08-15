from __future__ import annotations

from pathlib import Path


def template_root() -> Path:
    """Directory that contains copier.yml (repo root in dev, package data in a wheel)."""
    pkg = Path(__file__).resolve().parent
    if (pkg / "copier.yml").is_file():
        return pkg
    repo = pkg.parents[1]
    if (repo / "copier.yml").is_file():
        return repo
    raise RuntimeError("copier.yml not found; reinstall copier-formwork with template data")
