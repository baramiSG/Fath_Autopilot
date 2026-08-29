.PHONY: test lint typecheck

test:
	uv run pytest

lint:
	uv run ruff check src scripts
	uv run ruff format --check src scripts

typecheck:
	uv run mypy src/ scripts/
