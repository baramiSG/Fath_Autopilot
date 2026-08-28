# Fath Autopilot

Research-assistance platform repository. This checkout contains the TASK-001
foundation: a Python 3.11 package under `src/fath`, a uv-managed environment,
Alembic migrations, and a local Postgres 16 + Redis 7 service stack.

## Local development

1. Copy `.env.example` to `.env` and adjust placeholders if needed.
2. `uv sync --locked`
3. `docker compose up -d --build`
4. `uv run alembic upgrade head`
5. `make test`

Do not commit `.env`. Configuration keys in this slice are only `DATABASE_URL`,
`REDIS_URL`, and `FATH_ENV`.
