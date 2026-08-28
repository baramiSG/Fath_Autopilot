.PHONY: test lint typecheck

test:
	uv run pytest

lint:
	uv run ruff check src
	uv run ruff format --check src

typecheck:
	uv run mypy src/
