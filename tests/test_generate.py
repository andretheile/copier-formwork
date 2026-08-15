from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from copier_formwork.paths import template_root
from copier_formwork.server import copier_answers, generate_project

WIZARD = Path(__file__).resolve().parents[1] / "src" / "copier_formwork" / "static" / "wizard.html"


def _base(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "project_name": "demo-svc",
        "kind": "service",
        "git_host": "gitlab",
        "integration_branch": "dev",
        "runtime": "fastapi",
        "frontend": "vite",
        "database": "postgres",
        "orchestration": "none",
        "evals": "pytest",
        "observability": "none",
        "python_version": "3.12",
        "author_name": "Test",
    }
    data.update(overrides)
    return data


def _assert_generated_python_is_ruff_clean(dest: Path) -> None:
    ruff = Path(sys.executable).with_name("ruff")
    if not ruff.is_file():
        found = shutil.which("ruff")
        assert found, "ruff must be on PATH"
        ruff = Path(found)
    formatted = subprocess.run(
        [str(ruff), "format", "--check", dest / "src", dest / "tests"],
        check=False,
        capture_output=True,
        text=True,
    )
    linted = subprocess.run(
        [str(ruff), "check", dest / "src", dest / "tests"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert formatted.returncode == 0, formatted.stdout + formatted.stderr
    assert linted.returncode == 0, linted.stdout + linted.stderr


def test_template_root_contains_copier_yml() -> None:
    root = template_root()
    assert (root / "copier.yml").is_file()
    assert (root / "template" / "AGENTS.md.jinja").is_file()


def test_package_kind_forces_library_runtime() -> None:
    answers = copier_answers({"kind": "package", "runtime": "fastapi", "project_name": "x"})
    assert answers["runtime"] == "library"
    assert answers["frontend"] == "none"
    assert answers["database"] == "none"


def test_agent_kind_drops_frontend_and_database() -> None:
    answers = copier_answers(
        {
            "kind": "agent",
            "frontend": "vite",
            "database": "postgres",
            "project_name": "x",
        }
    )
    assert answers["frontend"] == "none"
    assert answers["database"] == "none"


def test_vite_frontend_forces_fastapi() -> None:
    answers = copier_answers(
        {"kind": "service", "frontend": "vite", "runtime": "cli", "project_name": "x"}
    )
    assert answers["runtime"] == "fastapi"


def test_wizard_mentions_copier_questions() -> None:
    html = WIZARD.read_text(encoding="utf-8")
    for key in (
        "project_name",
        "kind",
        "git_host",
        "integration_branch",
        "runtime",
        "frontend",
        "database",
        "orchestration",
        "evals",
        "observability",
    ):
        assert key in html


def test_generate_service_gitlab(tmp_path: Path) -> None:
    dest = tmp_path / "demo-svc"
    generate_project(dest, _base())
    assert "Apache License" in (dest / "LICENSE").read_text(encoding="utf-8")
    assert (dest / "src" / "demo_svc" / "domain" / "hello.py").is_file()
    assert (dest / "src" / "demo_svc" / "adapters" / "http" / "router.py").is_file()
    assert (dest / "src" / "demo_svc" / "adapters" / "postgres" / "ping.py").is_file()
    assert not (dest / "src" / "demo_svc" / "hello.py").exists()
    assert not (dest / "src" / "demo_svc" / "db.py").exists()
    assert (dest / "docker-compose.yml").is_file()
    assert (dest / "Dockerfile").is_file()
    assert (dest / "frontend" / "src" / "api.ts").is_file()
    compose = (dest / "docker-compose.yml").read_text(encoding="utf-8")
    assert "postgres:" in compose
    assert "web:" in compose
    api_ts = (dest / "frontend" / "src" / "api.ts").read_text(encoding="utf-8")
    assert "/health" in api_ts
    assert (dest / ".gitlab-ci.yml").is_file()
    assert not (dest / ".github").exists()
    assert not (dest / "ARCHITECTURE.md").exists()
    assert "```mermaid" in (dest / "docs" / "architecture" / "data.md").read_text(encoding="utf-8")
    assert "just check" in (dest / "AGENTS.md").read_text(encoding="utf-8")
    assert (dest / "tests" / "test_frontend_boundary.py").is_file()
    assert (dest / "tests" / "test_database_compose.py").is_file()
    assert (dest / "tests" / "test_ready.py").is_file()
    _assert_generated_python_is_ruff_clean(dest)


def test_generate_package_github(tmp_path: Path) -> None:
    dest = tmp_path / "demo-lib"
    generate_project(
        dest,
        _base(
            project_name="demo-lib",
            kind="package",
            git_host="github",
            integration_branch="main",
            runtime="library",
        ),
    )
    assert (dest / "src" / "demo_lib" / "hello.py").is_file()
    assert not (dest / "src" / "demo_lib" / "domain").exists()
    assert not (dest / "src" / "demo_lib" / "adapters").exists()
    assert not (dest / "src" / "demo_lib" / "api.py").exists()
    assert not (dest / "src" / "demo_lib" / "registry.py").exists()
    assert not (dest / "frontend").exists()
    assert not (dest / "Dockerfile").exists()
    assert not (dest / "docker-compose.yml").exists()
    assert (dest / ".github" / "workflows" / "ci.yml").is_file()
    assert not (dest / ".gitlab-ci.yml").exists()
    ci = (dest / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "${{ github.base_ref }}" in ci
    stripped = ci.replace("${{ github.base_ref }}", "").replace("${{ github.head_ref }}", "")
    assert "{{ github." not in stripped
    _assert_generated_python_is_ruff_clean(dest)


def test_generate_agent(tmp_path: Path) -> None:
    dest = tmp_path / "demo-agent"
    generate_project(dest, _base(project_name="demo-agent", kind="agent", runtime="cli"))
    assert (dest / "src" / "demo_agent" / "agent.py").is_file()
    assert (dest / "src" / "demo_agent" / "registry.py").is_file()
    assert (dest / "src" / "demo_agent" / "__main__.py").is_file()
    assert not (dest / "frontend").exists()
    assert not (dest / "src" / "demo_agent" / "db.py").exists()
    registry = (dest / "src" / "demo_agent" / "registry.py").read_text(encoding="utf-8")
    assert '"echo"' in registry
    _assert_generated_python_is_ruff_clean(dest)


def test_generate_service_api_only(tmp_path: Path) -> None:
    dest = tmp_path / "demo-api"
    generate_project(
        dest,
        _base(
            project_name="demo-api",
            frontend="none",
            database="none",
        ),
    )
    assert (dest / "src" / "demo_api" / "api.py").is_file()
    assert (dest / "Dockerfile").is_file()
    assert not (dest / "frontend").exists()
    assert not (dest / "src" / "demo_api" / "db.py").exists()
    assert (dest / "src" / "demo_api" / "domain" / "hello.py").is_file()
    assert (dest / "src" / "demo_api" / "adapters" / "http" / "router.py").is_file()
    assert not (dest / "src" / "demo_api" / "adapters" / "postgres").exists()
    assert not (dest / "tests" / "test_frontend_boundary.py").exists()
    assert not (dest / "tests" / "test_database_compose.py").exists()
    assert not (dest / "tests" / "test_ready.py").exists()
    compose = (dest / "docker-compose.yml").read_text(encoding="utf-8")
    assert "postgres:" not in compose
    assert "web:" not in compose
    _assert_generated_python_is_ruff_clean(dest)


def test_refuse_nonempty_destination(tmp_path: Path) -> None:
    dest = tmp_path / "taken"
    dest.mkdir()
    (dest / "stale.txt").write_text("nope", encoding="utf-8")
    try:
        generate_project(dest, _base(project_name="taken"))
    except ValueError as exc:
        assert "not empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")
