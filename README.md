# Copier Formwork

Copier templates with a mechanical architecture harness, plus a localhost questionnaire so you do not start from a blank folder.

Coding agents (Cursor, Claude Code, Codex) get a project that already has `just check`, architecture tests, living mermaid under `docs/architecture/`, and merge requests into `dev`.

## Quick start

```bash
uv sync --extra dev
uv run copier-formwork wizard
```

That binds **127.0.0.1**, opens the HTML wizard, and calls Copier when you click Generate.

Or from the CLI without the wizard:

```bash
uvx copier copy --trust path/to/copier-formwork ./my-new-project
```

## What a generated project includes

- `AGENTS.md` (Claude Code reads `CLAUDE.md` → `@AGENTS.md`)
- `just check` as the definition of done (ruff + pytest)
- Architecture tests: no root `ARCHITECTURE.md`; mermaid lives in `docs/architecture/`
- Registry tests for services/agents (every tool has `tests/test_tool_<name>.py`)
- GitHub or GitLab CI, including a job that rejects feature MRs aimed at `main` when you chose `dev`
- One green example (`hello()`, and an `echo` tool when kind is not a library)
- Service default: Vite frontend talks only through `frontend/src/api.ts`; Postgres is a Compose service behind FastAPI
- Service internals: modular monolith — `domain/` (rules) + `adapters/http/` (HTTP) + `adapters/postgres/` (data). Not a microservice mesh.

## Kinds

| Kind | You get |
|------|---------|
| Library | Installable package, smoke test, docs |
| Service | Modular FastAPI (domain + adapters), Compose, optional Vite SPA, optional Postgres |
| Agent | Tool registry, CLI, `echo` example |

Copier questions in `copier.yml` are the source of truth. The wizard must keep the same field names.

## Develop this repo

```bash
just check
```

`template/` is what Copier renders. `src/copier_formwork/` is the wizard and CLI.

## License

Apache License 2.0. See [LICENSE](LICENSE).
