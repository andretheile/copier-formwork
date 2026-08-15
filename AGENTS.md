# AGENTS.md

This repository is the Copier Formwork *template and wizard*, not a generated app.

## Commands

- `just check` — ruff + pytest
- `just wizard` — localhost questionnaire on 127.0.0.1:8765
- `uv run copier-formwork wizard --no-browser`

## Layout

- `copier.yml` — questions (source of truth)
- `template/` — files rendered into new projects
- `src/copier_formwork/` — CLI + Starlette wizard
- `src/copier_formwork/static/wizard.html` — single-file UI; field names must match `copier.yml`
- `tests/` — generate flavors into tmp dirs and assert layout

## Do not

- Put architecture mermaid in the generated README (keep it in `template/docs/architecture/`)
- Add wizard questions that are not Copier answers
- Bind the wizard to a public interface (localhost only)
- Invent a second template root

## Definition of done

`just check` is green. If you change `copier.yml`, update the wizard and a generate test.
