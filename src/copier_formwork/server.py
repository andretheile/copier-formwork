from __future__ import annotations

import json
import shutil
import tempfile
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from copier import run_copy
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route

from copier_formwork.paths import template_root

QUESTION_KEYS = (
    "project_name",
    "package_name",
    "description",
    "kind",
    "git_host",
    "integration_branch",
    "runtime",
    "frontend",
    "database",
    "orchestration",
    "evals",
    "observability",
    "python_version",
    "author_name",
)


def _wizard_html() -> Path:
    return Path(__file__).resolve().parent / "static" / "wizard.html"


def copier_answers(payload: dict[str, Any]) -> dict[str, Any]:
    data = {
        key: payload[key]
        for key in QUESTION_KEYS
        if key in payload and payload[key] not in (None, "")
    }
    name = str(data.get("project_name", "my-agent-service"))
    data.setdefault("package_name", name.replace("-", "_"))
    data.setdefault("description", "A well-formed project generated with copier-formwork.")
    data.setdefault("python_version", "3.12")
    data.setdefault("author_name", "TODO")
    if data.get("kind") != "service":
        data["frontend"] = "none"
        data["database"] = "none"
    if data.get("kind") == "package":
        data["runtime"] = "library"
    if data.get("frontend") == "vite":
        data["runtime"] = "fastapi"
    return data


@contextmanager
def staged_template() -> Iterator[Path]:
    """Copy copier.yml + template/ to a non-git dir so Copier uses the working tree."""
    root = template_root()
    with tempfile.TemporaryDirectory(prefix="copier-formwork-") as tmp:
        staging = Path(tmp) / "src"
        staging.mkdir()
        shutil.copy2(root / "copier.yml", staging / "copier.yml")
        shutil.copytree(root / "template", staging / "template")
        yield staging


def generate_project(destination: Path, payload: dict[str, Any]) -> Path:
    dest = destination.expanduser().resolve()
    if dest.exists() and dest.is_dir() and any(dest.iterdir()):
        raise ValueError(f"Destination is not empty: {dest}")
    if dest.exists() and dest.is_file():
        raise ValueError(f"Destination is a file: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with staged_template() as src:
        run_copy(
            str(src),
            str(dest),
            data=copier_answers(payload),
            defaults=True,
            unsafe=True,
            quiet=True,
        )
    return dest


async def index(_request: Request) -> FileResponse:
    return FileResponse(_wizard_html(), media_type="text/html")


async def generate(request: Request) -> Response:
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
    raw_dest = payload.get("destination")
    if not raw_dest:
        return JSONResponse({"error": "destination is required"}, status_code=400)
    try:
        path = generate_project(Path(str(raw_dest)), payload)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:  # noqa: BLE001 — surface Copier errors to the wizard
        return JSONResponse({"error": str(exc)}, status_code=500)
    return JSONResponse({"path": str(path)})


def create_app() -> Starlette:
    return Starlette(
        routes=[
            Route("/", index),
            Route("/api/generate", generate, methods=["POST"]),
        ]
    )


def serve_wizard(*, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    import uvicorn

    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Wizard binds locally only (127.0.0.1 / localhost / ::1)")
    url = (
        f"http://127.0.0.1:{port}/"
        if host in {"127.0.0.1", "localhost"}
        else f"http://[{host}]:{port}/"
    )
    if open_browser:
        webbrowser.open(url)
    uvicorn.run(create_app(), host=host, port=port, log_level="info")
