# TASK-001 — Repository Foundation: Scaffold, Environment, Database Baseline, Source Registry Schema, SHA-Bound CI Evidence

**Project:** FATH_AUTOPILOT · **Task ID:** TASK-001 · **Plan version:** v2 (remediation 1)
**Author role:** TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (plan_review_attempt 2 of 3) — NOT self-approved; authorizes no implementation until independent Sol review returns APPROVE.
**Branch when dispatched:** `task/TASK-001-repository-foundation` (cut from `main` after the controller merges the approved plan baseline).
**Remediation:** incorporates FATH-PR-001/002/003/005/006 corrections (see `REMEDIATION-1_ADJUDICATION.md`).

This plan is subordinate to canonical `docs/` authority (AMENDMENT-001 `docs/33` top of precedence, then `docs/24`, then the corpus) and to `BOOTSTRAP_PLAN.md` as reviewed. It creates no new requirements.

---

## 1. Objective

Create the minimal verifiable foundation on which every later bounded task builds: doc-16-conformant repository scaffold, reproducible uv-managed Python environment, runnable local service stack (Postgres 16 with Apache AGE + pgvector, Redis 7), typed configuration loading, Alembic migration baseline, and the Source Registry **schema** (structure only — NO seed data, see §5), with SHA-bound CI test evidence.

## 2. Authoritative references (read before implementing)

| Authority | Governs in this task |
|---|---|
| docs/33 AMENDMENT-001 | No Azure OpenAI SDK/endpoint/env in implementation/configuration (verifier item 2); no A100 assumption in implementation/configuration/sizing (item 1). This task introduces **no** LLM or GPU code. |
| docs/16 | **Canonical layout is binding as written** (doc-23 anti-drift rule: deviations require an ADR-style note WITH human approval — this task creates none). Module names: `safety/`, `budgets/`, `db/connection.py`, `db/migrations/`, `db/models/source_registry.py`, tests under `src/fath/tests/{fixtures,unit,integration}`. Root files per doc 16: `pyproject.toml`, `docker-compose.yml`, `README.md`. |
| docs/02 (as amended by 33) | Locked stack; single-Postgres decision; ADR supersession rule (human-approved per doc 23). |
| docs/22 §1 | Required extensions: uuid-ossp, vector, age. |
| docs/28 | Postgres 16, Redis 7, Alembic migration policy and migration test cycle, secrets rules (.env local only). |
| docs/03 | SourceRegistryRecord field contract, AccessDecision contract context, recommended indices. Seed VALUES are NOT fully established by authority — see §5. |
| docs/24 §1 | Source status enum with DB CHECK; textual source identifiers (`qatar_open_data`, …) in the canonical Week-1 sets. |
| docs/29 | `source_onboarding_checklists.source_id TEXT PRIMARY KEY REFERENCES sources(id)` — TEXT identifier model; onboarding checklist required before any `active` status. |
| docs/30 | Textual `source_id` convention in the candidate template and tier lists. |
| docs/23 | Week-1 done criterion "Source Registry table exists"; anti-drift rule (ADR + human approval). |
| Control plane: constitution §9/§19, review policy §§36–39, SG-TR-007 | CI as SHA-bound evidence (trusted gate NOT_CONFIGURED — see §9); uv; typing; no bare except; governed workflow. |
| BOOTSTRAP_PLAN.md (v2) §§4–10 | Identifier-model DERIVED resolution (§7), PROPOSED items (§4.4), CI posture (§9). |

## 3. Requirements traced (from REQUIREMENTS_TRACEABILITY.json)

FA-REQ-W1-001 (registry **schema + indices** portion only; seed data moved to TASK-006 gated on FA-OPEN-020), FA-REQ-W1-002 (status enum + CHECK — schema portion; guard logic is TASK-006), FA-REQ-W1-018 (doc-16 layout + conventions), FA-REQ-W1-019 (PG16 + extensions; Redis 7 roles), FA-REQ-W1-020 (Alembic upgrade/downgrade + cycle test), FA-REQ-CP-001 (CI as SHA-bound evidence), FA-REQ-CP-002 (uv, typing, exception hygiene), FA-REQ-CP-003 (governed Git workflow), FA-REQ-AM-001 (negative constraint only: no Azure OpenAI artifact in implementation/configuration).

## 4. Scope (what must change)

1. **Repository scaffold — exactly the doc-16 canonical layout** for every path created: `src/fath/__init__.py`; module packages with `__init__.py` for `config/`, `db/` (`connection.py`, `migrations/`, `models/`), `memory/`, `safety/`, `crawlers/`, `parsers/`, `extractors/`, `graph/`, `embeddings/`, `agents/`, `validators/`, `workflows/`, `events/`, `budgets/`, `ui/`, `api/`; tests under `src/fath/tests/{fixtures,unit,integration}`. Root files per doc 16: `pyproject.toml`, `docker-compose.yml`, `README.md` (pointing to `docs/` as authority). **Disclosed root-level additions (not module paths; not governed by the doc-16 module list):** `.gitignore`, `.env.example`, `alembic.ini`, `Makefile` (make targets serve docs 27/31 make-based workflow; targets here: test/lint/typecheck only — PROPOSED), `docker/postgres/Dockerfile` (PROPOSED packaging, §4.4), `.github/workflows/ci.yml` (control-plane requirement, disclosed in BOOTSTRAP_PLAN §9). No `sources/`, `trust/`, `budget/`, `audit/` or any other non-doc-16 module directory. `docs/` and `.delivery/` are untouched.
2. **Python environment:** `pyproject.toml` (Python 3.11 per PROPOSED baseline) + committed `uv.lock`. Dependencies limited to the BOOTSTRAP_PLAN §6 baseline (pydantic v2, pydantic-settings, SQLAlchemy 2, alembic, asyncpg, psycopg[binary] if needed for migrations, redis, PyYAML; dev: pytest, pytest-asyncio, ruff, mypy, gitleaks via CI, type stubs as needed). No FastAPI, LangGraph, Prefect, or any LLM/embedding dependency in this task.
3. **Tooling config:** ruff (lint + format), mypy strict on `src/`, pytest config.
4. **Local service stack (PROPOSED packaging per §4.4/PR-005):** `docker/postgres/Dockerfile` building Postgres 16 with Apache AGE and pgvector, with **exact pinned versions**: base image pinned by digest, AGE and pgvector pinned to exact release tags recorded in the Dockerfile (implementer selects the current stable releases compatible with PG16 and records them; changing a pin later is a reviewed change). `docker-compose.yml` with `postgres` (that image) and `redis:7-<pinned tag>`; named volumes; healthchecks.
5. **Typed configuration:** `src/fath/config/settings.py` (pydantic-settings) loading `DATABASE_URL`, `REDIS_URL`, `FATH_ENV`, and nothing speculative; `.env.example` with placeholders for exactly those keys — **no Azure OpenAI variable, no frontier-provider key yet** (those enter with the Week-2 LLM-client task).
6. **Database baseline:** async SQLAlchemy engine/session factory in `db/connection.py`; Alembic wired with `script_location = src/fath/db/migrations`; **migration 0001**: enable extensions (uuid-ossp, vector, age) and create `source_registry` matching the doc-03 SourceRegistryRecord field contract **with the DERIVED identifier model** (BOOTSTRAP_PLAN §7.4): `id TEXT PRIMARY KEY` (textual slug per docs 24 §1 / 29 / 30), all other doc-03 fields with their types/defaults/nullability, the doc-24 §1 status CHECK constraint, and doc-03 recommended indices. Full downgrade implemented.
7. **Pydantic contract:** `db/models/source_registry.py` — `SourceRegistryRecord` per doc-03 field contract with `source_id: str` (slug) per the DERIVED identifier resolution and the doc-24 §1 status field.
8. **CI (SHA-bound evidence):** `.github/workflows/ci.yml` per BOOTSTRAP_PLAN §9: `uv sync --frozen` → ruff check + format check → mypy → build pinned Postgres image + start services → `alembic upgrade head` → pytest → `alembic downgrade base` → `alembic upgrade head` → scoped AMENDMENT-001 scan (A8) → pinned-version gitleaks scan (A9). Fails on any error; no network calls in tests. **This CI is candidate-controlled test evidence bound to the exact SHA. It is NOT trusted verification: the trusted gate (protected CI + branch protection + receipts) is NOT_CONFIGURED and its setup is a roadmap item owned by Salim.**

## 5. Seed data — explicitly descoped (FATH-PR-001)

Authority establishes the seed **identities** (16 names + source classes + access preferences, doc 03; textual ids and tiers for most, docs 24 §1/30) but does **not** establish required record values: `base_url` and `reliability_tier` (required, no defaults in the doc-03 contract), rate limits per source, or collection modes per source. Doc 29 additionally requires a completed, human-approved onboarding checklist before ANY source is `active`, and doc 30's verifier requires YAML definition + checklist + rate limits before adding a candidate.

Therefore TASK-001 inserts **no seed rows** and creates **no `sources_seed.yaml` content**. Seed data, `config/sources_seed.yaml`, the seed loader, `source_onboarding_checklists` (doc-29 DDL), and Tier-0 activation evidence move to **TASK-006**, which is **gated on FA-OPEN-020**: a Salim-approved seed value table (per-source: textual id, name, class, base_url, api_base_url, reliability_tier, collection mode, rate limits, status) plus approved onboarding checklists for the three Tier-0 sources. Until FA-OPEN-020 is resolved, dispatching TASK-006 is `BLOCKED_FOR_SALIM`. No test in TASK-001 may fabricate seed records as if they were authoritative; contract-test fixtures are explicitly synthetic and labeled as such.

## 6. Acceptance criteria and oracles

| # | Criterion | Oracle class / verification |
|---|---|---|
| A1 | `uv sync --frozen` succeeds from clean checkout; `uv.lock` committed | SPECIFIED (SG-TR-007); CI step |
| A2 | `docker compose up -d` yields healthy postgres + redis; `SELECT extname FROM pg_extension` after migration contains uuid-ossp, vector, age | SPECIFIED (docs 22 §1, 28); integration test + CI |
| A3 | `alembic upgrade head` → `downgrade base` → `upgrade head` all succeed (doc-28 cycle) | SPECIFIED (doc 28); CI migration-cycle step |
| A4 | `source_registry` matches the doc-03 field contract with `id TEXT PRIMARY KEY` per the DERIVED identifier resolution, doc-24 §1 status CHECK, doc-03 indices; negative test: INSERT with status `bogus` rejected by the database | SPECIFIED (docs 03, 24 §1) + DERIVED (identifier model, flagged FA-OPEN-021 for reviewer confirmation); schema-reflection test + negative test |
| A5 | **Layout conformance:** every path created by this task matches the doc-16 canonical layout exactly; the only root-level additions are the §4.1 disclosed list; no non-doc-16 module directory exists under `src/fath/` | SPECIFIED (doc 16; doc-23 anti-drift); scripted tree comparison against the doc-16 listing, run in CI |
| A6 | `SourceRegistryRecord` validates a **synthetic, clearly-labeled** golden-positive fixture and rejects golden-negative fixtures (missing required field, invalid enum, invalid URL). Fixtures are marked `SYNTHETIC-TEST-FIXTURE — not seed data, not authority` | SPECIFIED (doc-03 contract); contract tests |
| A7 | ruff (lint+format) and mypy strict pass over `src/` | SPECIFIED (SG-TR-007); CI steps |
| A8 | **Scoped AMENDMENT-001 scan:** no `A100` and no Azure OpenAI SDK/endpoint/deployment/env-var reference in implementation/configuration artifacts — scan set: `src/`, `docker/`, `.github/`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `Makefile`, `alembic.ini`, `.env.example`; **explicit exclusions:** `docs/` (canonical historical documents legitimately contain the terms), `.delivery/` (governance records), `README.md` citations of docs | SPECIFIED (docs/33 verifier items 1–2, scoped per its own text: "implementation, configuration, or sizing"); scripted scan in CI |
| A9 | **Secret scan:** pinned-version gitleaks (PROPOSED tool choice) run over the full candidate tree passes; `.env` is git-ignored (test); `.env.example` contains placeholders only | SPECIFIED intent (doc 28 secrets rules; SG-TR-006) with PROPOSED tooling; CI step + gitignore test |
| A10 | CI green on the exact candidate SHA, recorded as **SHA-bound test evidence** (explicitly NOT a trusted-gate receipt; trusted gate NOT_CONFIGURED) | Control-plane review policy §§36–39; CI run URL bound to SHA |
| A11 | **Functional extension checks:** a test creates a table with a `vector(1024)` column and an HNSW index, and creates an AGE graph and runs a minimal cypher query, both successfully | SPECIFIED (docs 22 §1, 02); integration tests |

## 7. Implementation sequence (bounded)

1. Scaffold exactly per doc-16 + disclosed root additions; pyproject + uv.lock + tooling configs (A1, A5, A7 foundations).
2. Postgres Dockerfile with recorded pins + compose + healthchecks (A2).
3. Settings + `.env.example` (A8/A9 constraints).
4. `db/connection.py` + Alembic wiring + migration 0001 with downgrade (A3, A4).
5. `SourceRegistryRecord` + synthetic contract fixtures (A6).
6. Tests: schema reflection, negative status, migration cycle, extension presence, functional extension checks (A11), layout-conformance script (A5).
7. CI workflow incl. scoped scan + gitleaks; verify green on push (A8–A10).
8. Confirm, Validate, Test; produce evidence; create immutable candidate commit.

**What must remain unchanged:** `docs/` (read-only authority); `.delivery/plans/` and `.delivery/reviews/` (governance artifacts); no history rewrites; no seed rows anywhere.

## 8. Dependencies and blockers

- Dependencies: none (first implementation task). Requires only Docker + uv on the runner/workstation; no GPU, no external API, no credential.
- Blockers: none for TASK-001 as descoped. FA-OPEN-020 gates TASK-006 (not this task).

## 9. Stop conditions (stop and surface; do not guess)

1. Pinned AGE or pgvector releases cannot be built/loaded against Postgres 16 → STOP; surface pin options to the controller; do not switch Postgres major version (doc 28).
2. Any schema field of the doc-03 contract proves ambiguous against doc 24 §1 / doc 29 beyond the documented FA-OPEN-021 resolution → STOP; record; do not invent.
3. Any acceptance criterion can only pass by weakening an oracle → STOP (oracle policy §38).
4. Any need arises for a module path, schema, event type, or component not defined in the docs folder → STOP; doc-23 anti-drift requires an ADR-style note WITH human (Salim) approval before implementation.
5. CI platform unusable for SHA-bound runs → STOP; surface to controller.

## 10. Test and evidence expectations

- Tests per §6 under `src/fath/tests/` (doc-16 location); all runnable via `make test` and in CI; no network access; fixed seeds where randomness exists; fixtures labeled synthetic.
- Evidence for review: CI run URL/output bound to the candidate SHA (labeled SHA-bound evidence, not trusted receipt); local `alembic` cycle transcript; `pg_extension` listing; functional extension check output; layout-comparison output; scoped-scan and gitleaks outputs. Recorded under `.delivery/evidence/TASK-001/` by the implementer.

## 11. Completion conditions

All acceptance criteria A1–A11 pass with recorded evidence; one immutable candidate commit on `task/TASK-001-repository-foundation`; candidate SHA reported; independent implementation review (Sol seat) receives the exact SHA; no self-approval; merge only after APPROVE and gate satisfaction recorded in BUILD_STATE (with trusted-gate status truthfully recorded as NOT_CONFIGURED until Salim configures the protected mechanism).

## 12. Plan identity and review

- Plan path: `.delivery/plans/FATH-BOOTSTRAP/TASK-001_PLAN.md` (v2); SHA-256 recorded in the commit/handoff over this exact content.
- Reviewer: `plan-reviewer` (GPT-5.6 Sol, read-only, fresh context); outcomes APPROVE / REJECT / BLOCKED; attempt 2 of max 3.
