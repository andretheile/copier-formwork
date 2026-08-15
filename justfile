set dotenv-load := false

check:
    uv run ruff format --check src tests
    uv run ruff check src tests
    uv run pytest

fmt:
    uv run ruff format src tests
    uv run ruff check --fix src tests

test:
    uv run pytest

wizard:
    uv run copier-formwork wizard
