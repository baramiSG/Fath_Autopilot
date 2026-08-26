# TASK-001 — Repository Foundation: Scaffold, Environment, Database Baseline, Source Registry Schema and Seeds, Deterministic CI

**Project:** FATH_AUTOPILOT · **Task ID:** TASK-001 · **Plan version:** v1
**Author role:** TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (plan_review_attempt 1) — NOT self-approved; authorizes no implementation until independent Sol review returns APPROVE.
**Branch when dispatched:** `task/TASK-001-repository-foundation` (cut from `main` after the controller merges the approved plan baseline).

This plan is subordinate to canonical `docs/` authority (AMENDMENT-001 `docs/33` top of precedence, then `docs/24`, then the corpus) and to `BOOTSTRAP_PLAN.md` as reviewed. It creates no new requirements.

---

## 1. Objective

Create the minimal verifiable foundation on which every later bounded task builds: canonical repository scaffold, reproducible uv-managed Python environment, runnable local service stack (Postgres 16 with Apache AGE + pgvector, Redis 7), typed configuration loading, Alembic migration baseline, the Source Registry schema with its 16 canonical seeds and status discipline, and deterministic CI bound to the exact commit SHA.

## 2. Authoritative references (read before implementing)

| Authority | Governs in this task |
|---|---|
| docs/33 AMENDMENT-001 | No Azure OpenAI SDK/endpoint/env anywhere (verifier item 2); no A100 assumption (item 1). This task introduces **no** LLM or GPU code. |
| docs/16 | Canonical repository layout, module boundaries, coding + test conventions. |
| docs/02 (as amended by 33) | Locked stack; single-Postgres decision; ADR supersession rule. |
| docs/22 §1 | Required extensions: uuid-ossp, vector, age. |
| docs/28 | Postgres 16, Redis 7, Alembic migration policy and migration test cycle, secrets rules (.env local only). |
| docs/03 | SourceRegistryRecord contract, 16 initial registry seeds, recommended indices. |
| docs/24 §1 | Source status enum (candidate, candidate_manual_review, approved_inactive, active, suspended, quarantined, retired) with DB CHECK; Week-1 active set EXACTLY qatar_open_data, world_bank, gdelt; al_meezan, qcb, qse, invest_qatar = candidate_manual_review. |
| docs/23 | Week-1 done criteria touching this task (registry table with seeds); anti-drift rule. |
| Control plane: constitution §9/§19, review policy, SG-TR-007 | Deterministic CI; uv; typing; no bare except; governed workflow. |
| BOOTSTRAP_PLAN.md §§4–10 | Naming resolution (physical table `source_registry`), CI pipeline definition, dependency baseline, PROPOSED Python 3.11 / GitHub Actions / ruff+mypy+pytest / SQLAlchemy 2 + asyncpg. |

## 3. Requirements traced (from REQUIREMENTS_TRACEABILITY.json)

FA-REQ-W1-001 (registry schema + 16 seeds + indices — schema/seed portion), FA-REQ-W1-002 (status enum + CHECK — schema portion; guard logic is TASK-006), FA-REQ-W1-003 (exact Week-1 active set — seed portion), FA-REQ-W1-018 (doc-16 layout + conventions), FA-REQ-W1-019 (PG16 + extensions; Redis 7 roles), FA-REQ-W1-020 (Alembic upgrade/downgrade + cycle test), FA-REQ-CP-001 (deterministic CI), FA-REQ-CP-002 (uv, typing, exception hygiene), FA-REQ-CP-003 (governed Git workflow), FA-REQ-AM-001 (negative constraint only: no Azure OpenAI artifact may be introduced).

## 4. Scope (what must change)

1. **Repository scaffold** per doc-16 layout: `src/fath/` package with `__init__.py` and the Week-1 module directories as empty typed packages (config, db, sources, crawlers, trust, events, memory, budget, audit, workflows, api, agents — names exactly per doc 16); `tests/` mirroring; `docker/`; `migrations/`; `scripts/`; `Makefile`; root `README.md` pointing to `docs/` as authority; `.gitignore` (includes `.env`).
2. **Python environment:** `pyproject.toml` (Python 3.11 per PROPOSED baseline) + committed `uv.lock`. Dependencies limited to the BOOTSTRAP_PLAN §6 baseline (pydantic v2, pydantic-settings, SQLAlchemy 2, alembic, asyncpg, psycopg[binary] if needed for migrations, redis, PyYAML; dev: pytest, pytest-asyncio, ruff, mypy, types stubs as needed). No FastAPI, LangGraph, Prefect, or any LLM/embedding dependency in this task.
3. **Tooling config:** ruff (lint + format), mypy strict on `src/`, pytest config.
4. **Local service stack:** `docker/postgres/Dockerfile` building a pinned Postgres 16 image with Apache AGE and pgvector compiled/installed (versions pinned by tag/digest); `docker-compose.yml` with `postgres` (that image) and `redis:7-<pinned>`; named volumes; healthchecks.
5. **Typed configuration:** `src/fath/config/settings.py` (pydantic-settings) loading `DATABASE_URL`, `REDIS_URL`, `FATH_ENV`, and nothing speculative; `.env.example` with placeholders for exactly those keys — **no Azure OpenAI variable, no frontier-provider key yet** (those enter with the Week-2 LLM-client task).
6. **Database baseline:** async SQLAlchemy engine/session factory; Alembic wired to settings; **migration 0001**: enable extensions (uuid-ossp, vector, age) and create `source_registry` (physical name per BOOTSTRAP_PLAN §7 naming resolution) matching the doc-03 SourceRegistryRecord contract, with the doc-24 §1 status CHECK constraint and doc-03 recommended indices. Full downgrade implemented.
7. **Pydantic contract:** `SourceRegistryRecord` model exactly per doc-03 (field names, types, constraints), with the doc-24 §1 status enum.
8. **Seeds:** deterministic, idempotent seed script (`scripts/seed_source_registry.py`, invoked via `make seed`) inserting the 16 doc-03 seeds with statuses per doc-24 §1 (exactly 3 active; al_meezan, qcb, qse, invest_qatar as candidate_manual_review; remainder per doc-03/30). Re-running changes nothing.
9. **Deterministic CI:** `.github/workflows/ci.yml` per BOOTSTRAP_PLAN §9: `uv sync --frozen` → ruff check + format check → mypy → build pinned Postgres image + start services → `alembic upgrade head` → pytest → `alembic downgrade base` → `alembic upgrade head`; fails on any error; no network calls in tests.

## 5. Explicitly OUT of scope

Access Guard logic and decision persistence (TASK-006); audit log (TASK-002); raw archive/MinIO (TASK-003); event bus (TASK-004); trust boundary (TASK-005); crawlers (TASK-007/008); budgets (TASK-009); facts (TASK-010); workflows (TASK-011); FastAPI/SSE (TASK-012); frontend (TASK-013); any LLM client, embedding, OCR, or GPU-touching code (Week 2+, per AMENDMENT-001 constraints); any table beyond `source_registry`; branch-protection configuration (Salim, repo admin); any edit to `docs/`.

## 6. Acceptance criteria and oracles (all SPECIFIED oracle class)

| # | Criterion | Oracle / verification |
|---|---|---|
| A1 | `uv sync --frozen` succeeds from clean checkout | CI step; lockfile committed |
| A2 | `docker compose up -d` yields healthy postgres + redis; `SELECT extname FROM pg_extension` after migration contains uuid-ossp, vector, age | Integration test + CI service startup |
| A3 | `alembic upgrade head` → `downgrade base` → `upgrade head` all succeed (doc-28 cycle) | CI migration-cycle step; test asserting cycle |
| A4 | `source_registry` matches doc-03 contract (columns, nullability, defaults, indices) and enforces doc-24 §1 status CHECK | Schema reflection test + negative test: INSERT with status `bogus` rejected by the database |
| A5 | Seed run inserts exactly 16 records; exactly `qatar_open_data`, `world_bank`, `gdelt` active; `al_meezan`, `qcb`, `qse`, `invest_qatar` candidate_manual_review; second run is a no-op | Seed test with count/status assertions run twice |
| A6 | `SourceRegistryRecord` validates all 16 seeds; rejects missing required field and invalid enum (golden-negative fixtures) | Contract tests |
| A7 | ruff (lint+format) and mypy strict pass over `src/` | CI steps |
| A8 | Repo-wide scan finds no Azure OpenAI SDK/endpoint/deployment/env reference and no A100 reference (AMENDMENT-001 verifier items 1–2) | CI grep step + reviewer inspection |
| A9 | No secret in the repo; `.env` git-ignored; `.env.example` placeholders only | Reviewer inspection + gitignore test |
| A10 | CI green on the exact candidate SHA | GitHub Actions run bound to SHA |

## 7. Implementation sequence (bounded)

1. Scaffold + pyproject + uv.lock + tooling configs (A1, A7 foundations).
2. Postgres Dockerfile + compose + healthchecks (A2).
3. Settings + `.env.example` (A9; amendment constraint).
4. SQLAlchemy engine + Alembic wiring + migration 0001 with downgrade (A3, A4).
5. `SourceRegistryRecord` + seeds script (A5, A6).
6. Tests (contract, schema reflection, negative status, seed idempotency, migration cycle, extension presence).
7. CI workflow; verify green locally-equivalent, then on push (A8, A10).
8. Confirm, Validate, Test; produce evidence; create immutable candidate commit.

**What must remain unchanged:** `docs/` (read-only authority); `.delivery/plans/` (planning artifacts); no history rewrites.

## 8. Dependencies and blockers

- Dependencies: none (first implementation task). Requires only Docker + uv on the runner/workstation; no GPU, no external API, no credential.
- Blockers: none. FA-OPEN items 009/010/011/012/018/019 do not touch this task.

## 9. Stop conditions (stop and surface; do not guess)

1. Pinned AGE or pgvector versions cannot be built against Postgres 16 → STOP; surface options (different pinned minor, alternative pinned base) to the controller; do not switch Postgres major version (SPECIFIED by doc 28).
2. Any doc-03 seed field is ambiguous against the doc-24 status enum → STOP; record the conflict; do not invent values.
3. Any acceptance criterion can only pass by weakening an oracle (e.g. dropping the CHECK, loosening a contract) → STOP (oracle policy §38).
4. CI platform unusable for SHA-bound runs → STOP; surface to controller.

## 10. Test and evidence expectations

- Tests per §6 committed under `tests/` mirroring doc-16 layout; all runnable via `make test` and in CI; no network access; fixed seeds where randomness exists.
- Evidence for review: CI run URL/output bound to the candidate SHA; local `alembic` cycle transcript; seed-run output (counts + statuses); `pg_extension` listing; repo scan output for A8. Evidence recorded under `.delivery/evidence/TASK-001/` by the implementer.

## 11. Completion conditions

All acceptance criteria A1–A10 pass with recorded evidence; one immutable candidate commit on `task/TASK-001-repository-foundation`; candidate SHA reported; independent implementation review (Sol seat) receives the exact SHA; no self-approval; merge only after APPROVE and gate satisfaction recorded in BUILD_STATE.

## 12. Plan identity and review

- Plan path: `.delivery/plans/FATH-BOOTSTRAP/TASK-001_PLAN.md`; SHA-256 recorded in the commit/handoff over this exact content.
- Reviewer: `plan-reviewer` (GPT-5.6 Sol, read-only, fresh context); outcomes APPROVE / REJECT / BLOCKED; attempt 1 of max 3.
