# TASK-001 — Repository Foundation: Scaffold, Environment, Database Baseline, Source Registry Schema, SHA-Bound CI Evidence

**Project:** FATH_AUTOPILOT · **Task ID:** TASK-001 · **Plan version:** v3 (final correction)
**Author role:** TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (plan_review_attempt 3 of 3 — final autonomous attempt) — NOT self-approved; authorizes no implementation until independent Sol review returns APPROVE.
**Branch when dispatched:** `task/TASK-001-repository-foundation` (cut from `main` after the controller merges the approved plan baseline).
**Remediation lineage:** v2 corrections per `REMEDIATION-1_ADJUDICATION.md`; v3 corrections per `REMEDIATION-2_ADJUDICATION.md` (FATH-P2-001/002/003/004).

This plan is subordinate to canonical `docs/` authority (AMENDMENT-001 `docs/33` top of precedence, then `docs/24`, then the corpus) and to `BOOTSTRAP_PLAN.md` (v3) as reviewed. It creates no new requirements.

---

## 1. Objective

Create the minimal verifiable foundation on which every later bounded task builds: doc-16-conformant repository scaffold, reproducible uv-managed Python environment, runnable local service stack (Postgres 16 with Apache AGE + pgvector, Redis 7), typed configuration loading, Alembic migration baseline, and the Source Registry **schema** (structure only — zero rows, no seed artifacts; §5), with SHA-bound CI test evidence.

## 2. Authoritative references (read before implementing)

| Authority | Governs in this task |
|---|---|
| docs/33 AMENDMENT-001 | No Azure OpenAI SDK/endpoint/env in implementation/configuration (verifier item 2); no A100 assumption in implementation/configuration/sizing (item 1). This task introduces **no** LLM or GPU code. |
| docs/16 | **Canonical layout is binding as written** (doc-23 anti-drift rule: deviations require an ADR-style note WITH human approval — this task creates none). Module names: `safety/`, `budgets/`, `db/connection.py`, `db/migrations/`, `db/models/source_registry.py`, tests under `src/fath/tests/{fixtures,unit,integration}`. Root files per doc 16: `pyproject.toml`, `docker-compose.yml`, `README.md`. |
| docs/02 (as amended by 33) | Locked stack; single-Postgres decision; ADR supersession rule (human-approved per doc 23). |
| docs/22 §1 + table list | Required extensions: uuid-ossp, vector, age; canonical table name `source_registry`. |
| docs/28 | Postgres 16, Redis 7, Alembic migration policy and migration test cycle, secrets rules (.env local only). |
| docs/03 | SourceRegistryRecord field contract (`source_id: UUID` storage identity), AccessDecision context, recommended indices. Seed VALUES not established — §5. |
| docs/04 §Foreign keys; docs/21 DDL | `raw_archive.source_id → source_registry.source_id`; `source_id UUID NOT NULL REFERENCES source_registry(source_id)` — the UUID storage-identity contracts the schema must keep satisfiable. |
| docs/24 §1, §§4–5, §8 | Source status enum + DB CHECK; textual source identifiers in the canonical Week-1 sets; event/UI payloads carry `source_id: str` (textual) alongside `source_name`. |
| docs/29 | `source_onboarding_checklists.source_id TEXT ... REFERENCES sources(id)`; TEXT identifier in compliance tables (created in TASK-006, but the identity model must support them). |
| docs/30 | Textual `source_id` in candidate template and tier lists. |
| docs/23 | Week-1 done criterion "Source Registry table exists"; anti-drift rule (ADR + human approval). |
| Control plane: constitution §§9/19, review policy §§36–46, SG-TR-007 | CI as SHA-bound evidence; candidates halt at REVIEW_APPROVED until the trusted gate is verified active (§11); uv; typing; governed workflow. |
| BOOTSTRAP_PLAN.md (v3) §§4, 7.4, 9, 12 | Dual-identity model (§7.4), PROPOSED items (§4.4), CI + gate sequencing (§9). |

## 3. Requirements traced (from REQUIREMENTS_TRACEABILITY.json)

FA-REQ-W1-001 (registry **schema + indices** portion only; seed data is TASK-006 gated on FA-OPEN-020), FA-REQ-W1-002 (status enum + CHECK — schema portion), FA-REQ-W1-018 (doc-16 layout), FA-REQ-W1-019 (PG16 + extensions; Redis 7), FA-REQ-W1-020 (Alembic cycle), FA-REQ-CP-001 (CI as SHA-bound evidence), FA-REQ-CP-002 (uv, typing), FA-REQ-CP-003 (governed workflow; halt at REVIEW_APPROVED pre-gate), FA-REQ-AM-001 (negative constraint: no Azure OpenAI artifact in implementation/configuration).

## 4. Scope (what must change)

1. **Repository scaffold — doc-16 canonical layout** for every path created (the full four-set path oracle is A5/§6.1): `src/fath/__init__.py`; packages `config/`, `db/` (`connection.py`, `migrations/`, `models/`), `memory/`, `safety/`, `crawlers/`, `parsers/`, `extractors/`, `graph/`, `embeddings/`, `agents/`, `validators/`, `workflows/`, `events/`, `budgets/`, `ui/`, `api/`; tests under `src/fath/tests/{fixtures,unit,integration}`; root `pyproject.toml`, `docker-compose.yml`, `README.md`. Disclosed root-level additions (not module paths): `.gitignore`, `.env.example`, `alembic.ini`, `Makefile` (test/lint/typecheck targets only — PROPOSED), `docker/postgres/Dockerfile` (PROPOSED packaging, §4.4), `.github/workflows/ci.yml`. `docs/` and `.delivery/` untouched.
2. **Python environment:** `pyproject.toml` (Python 3.11 PROPOSED baseline) + committed `uv.lock`. Dependencies limited to the BOOTSTRAP_PLAN §6 baseline. No FastAPI, LangGraph, Prefect, or any LLM/embedding dependency.
3. **Tooling config:** ruff (lint + format), mypy strict on `src/`, pytest config.
4. **Local service stack (PROPOSED packaging per BOOTSTRAP_PLAN §4.4):** `docker/postgres/Dockerfile` — Postgres 16 base pinned by digest; AGE and pgvector pinned to exact release tags recorded in the Dockerfile. `docker-compose.yml` with that image + pinned `redis:7` tag; named volumes; healthchecks.
5. **Typed configuration:** `src/fath/config/settings.py` (pydantic-settings) loading `DATABASE_URL`, `REDIS_URL`, `FATH_ENV` only; `.env.example` with placeholders for exactly those keys — no Azure OpenAI variable, no frontier-provider key (those enter with the Week-2 LLM-client task).
6. **Database baseline:** async SQLAlchemy engine/session factory in `db/connection.py`; Alembic with `script_location = src/fath/db/migrations`; **migration 0001**: enable the three extensions and create `source_registry` per the **dual-identity model** (BOOTSTRAP_PLAN §7.4): `source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4()` (docs 03/04/21 storage identity), `slug TEXT NOT NULL UNIQUE` (textual identifier used by docs 24 §1/29/30/06; column name PROPOSED), all other doc-03 fields with their types/defaults/nullability, doc-24 §1 status column + CHECK, doc-03 recommended indices. **The migration inserts zero rows.** Full downgrade implemented. No other table in this task (doc-29 compliance tables arrive with TASK-006 and will FK `TEXT REFERENCES source_registry(slug)` — recorded here as the forward contract, not created now).
7. **Pydantic contract:** `db/models/source_registry.py` — `SourceRegistryRecord` per the doc-03 field contract verbatim (`source_id: UUID` with uuid4 default) **plus** `slug: str` and the doc-24 §1 `status` field (both additions cited in §7.4 of the bootstrap plan; the corpus itself amends this model — doc 24 §1 adds `status`).
8. **CI (SHA-bound evidence):** `.github/workflows/ci.yml` per BOOTSTRAP_PLAN §9: `uv sync --frozen` → ruff check + format check → mypy → build pinned image + start services → `alembic upgrade head` → **zero-row check (A12)** → pytest → `alembic downgrade base` → `alembic upgrade head` → zero-row check again → expected-schema comparison (A4) → expected-tree check (A5) → seed-artifact absence check (A13) → scoped AMENDMENT-001 scan (A8) → pinned gitleaks scan (A9). Fails on any error; no network calls in tests. **Classification: candidate-controlled test evidence bound to the exact SHA — never trusted verification. Trusted gates are NOT_CONFIGURED / branch protection NOT_VERIFIED (BUILD_STATE); this candidate halts at REVIEW_APPROVED and is NOT merge-eligible until the §11 gate sequencing completes.**

## 5. Seed data — descoped AND negatively enforced (FATH-PR-001, FATH-P2-002)

Authority establishes seed identities but not the required values (`base_url`, `reliability_tier` — mandatory doc-03 fields with no defaults — plus per-source rate limits and collection modes), and doc 29 requires human-approved onboarding checklists before activation. Seeds are therefore TASK-006 scope, gated on **FA-OPEN-020** (Salim-approved seed value table + Tier-0 checklists; dispatch without it is `BLOCKED_FOR_SALIM`).

For THIS candidate the boundary is mechanically enforced, not merely stated:

- Migrations insert zero rows (A12: `SELECT COUNT(*) FROM source_registry` = 0 after a fresh `upgrade head`, and again after the downgrade/upgrade cycle).
- No seed artifact exists in the candidate (A13): no `src/fath/config/sources_seed.yaml` (it is in A5's PROHIBITED set for this task even though doc 16 lists it — it belongs to TASK-006), no `execution_rules.yaml`, no module whose path or name matches a seed loader (`git ls-files` scan for `*seed*` under `src/` must return nothing).
- Test fixtures are synthetic and non-persistent: fixture files carry the marker `SYNTHETIC-TEST-FIXTURE — not seed data, not authority` (scanned mechanically), and any test that inserts a `source_registry` row does so inside a transaction that is rolled back or against the ephemeral CI database; the A12 zero-row checks run on fresh schema state, independent of test execution.

## 6. Acceptance criteria and oracles

### 6.1 A5 expected-tree oracle (four path sets — FATH-P2-003)

The candidate commits a machine-readable manifest `src/fath/tests/fixtures/expected_tree.json` (hand-derived from doc 16 and this plan — not generated from the working tree) with four sets, checked mechanically by a test/CI script:

- **REQUIRED** (must exist; each entry cites doc 16 or this plan §4): `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `README.md`, `src/fath/__init__.py`, the 16 module packages listed in §4.1 each with `__init__.py`, `src/fath/config/settings.py`, `src/fath/db/connection.py`, `src/fath/db/migrations/` (env + one versioned migration), `src/fath/db/models/source_registry.py`, `src/fath/tests/fixtures/`, `src/fath/tests/unit/`, `src/fath/tests/integration/`.
- **PERMITTED** (may exist; the disclosed additions and mechanical by-products): `.gitignore`, `.env.example`, `alembic.ini`, `Makefile`, `docker/postgres/**`, `.github/workflows/ci.yml`, `__init__.py` files, migration version files, test files under `src/fath/tests/**`, the manifest itself.
- **DEFERRED** (canonical in doc 16 but NOT created by TASK-001; their absence must not fail the check, their presence outside PERMITTED does): `frontend/**`, the doc-16 per-module implementation files (e.g. `crawlers/base.py`, `safety/trust_boundary.py`), `src/fath/config/execution_rules.yaml`, `docs/adr/`.
- **PROHIBITED** (must NOT exist in this candidate): any directory under `src/fath/` not in the doc-16 module list (e.g. `sources/`, `trust/`, `budget/`, `audit/`, `llm/`), top-level `tests/` or `migrations/`, `src/fath/config/sources_seed.yaml`, any `*seed*` path under `src/`.

Check: every REQUIRED path exists; no PROHIBITED path exists; every path present in the candidate (excluding `docs/`, `.delivery/`, `.git/`) is in REQUIRED ∪ PERMITTED.

### 6.2 Criteria table

| # | Criterion | Oracle class / verification |
|---|---|---|
| A1 | `uv sync --frozen` succeeds from clean checkout; `uv.lock` committed | SPECIFIED (SG-TR-007); CI step |
| A2 | `docker compose up -d` yields healthy postgres + redis; `SELECT extname FROM pg_extension` after migration contains uuid-ossp, vector, age | SPECIFIED (docs 22 §1, 28); integration test + CI |
| A3 | `alembic upgrade head` → `downgrade base` → `upgrade head` all succeed (doc-28 cycle) | SPECIFIED (doc 28); CI step |
| A4 | **Expected-schema comparison:** a committed fixture `src/fath/tests/fixtures/expected_schema.json` — hand-derived from the cited doc sections (each column/constraint entry carries its citation: doc 03 fields, docs 03/04/21 UUID `source_id` PK, docs 24 §1 status + CHECK, §7.4 slug UNIQUE, doc-03 indices), NOT generated from the SQLAlchemy models — is compared mechanically against `information_schema`/`pg_catalog` after `upgrade head`: table name, column names, data types, nullability, defaults presence, PK, UNIQUE, CHECK, indices. Negative test: INSERT with status `bogus` rejected | SPECIFIED elements + DERIVED dual-identity (FA-OPEN-021; reviewer confirms); independent mechanical comparison (oracle policy: fixture independent of implementation code) |
| A5 | **Expected-tree conformance** per §6.1 four-set manifest | SPECIFIED base (doc 16) + task-scoped sets from this plan; mechanical script in CI |
| A6 | `SourceRegistryRecord` (doc-03 contract + slug + status per §7.4) validates a synthetic golden-positive fixture and rejects golden-negatives (missing required field, invalid enum, invalid URL, invalid status). Fixtures carry the synthetic marker | SPECIFIED (doc-03 contract) + DERIVED additions (FA-OPEN-021); contract tests |
| A7 | ruff (lint+format) and mypy strict pass over `src/` | SPECIFIED (SG-TR-007); CI steps |
| A8 | **Scoped AMENDMENT-001 scan:** no `A100` / Azure OpenAI SDK/endpoint/deployment/env reference in: `src/`, `docker/`, `.github/`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `Makefile`, `alembic.ini`, `.env.example`. Exclusions: `docs/`, `.delivery/`, README doc citations | SPECIFIED (docs/33 verifier items 1–2, scoped per its own "implementation, configuration, or sizing" text); scripted CI scan |
| A9 | **Secret scan:** pinned-version gitleaks (PROPOSED tool) over the candidate tree passes; `.env` git-ignored (test); `.env.example` placeholders only | SPECIFIED intent (doc 28; SG-TR-006) + PROPOSED tooling; CI step + test |
| A10 | CI green on the exact candidate SHA, recorded as **SHA-bound test evidence** (never trusted acceptance; gates per §11) | Review policy §§36–46; CI run URL bound to SHA |
| A11 | **Functional extension checks:** create a table with `vector(1024)` column + HNSW index; create an AGE graph + run a minimal cypher query — both succeed | SPECIFIED (docs 22 §1, 02); integration tests |
| A12 | **Zero-seed state:** `source_registry` row count = 0 after fresh `upgrade head` AND after the downgrade/upgrade cycle | SPECIFIED boundary (seeds are TASK-006/FA-OPEN-020); mechanical SQL check in CI, run on fresh schema before/independent of tests |
| A13 | **No seed artifact:** `git ls-files` shows no `src/fath/config/sources_seed.yaml`, no `*seed*` path under `src/`; fixture files carry the synthetic marker | Same; mechanical ls-files + marker scan in CI |

## 7. Implementation sequence (bounded)

1. Scaffold per §4.1 + pyproject + uv.lock + tooling configs (A1, A7).
2. Postgres Dockerfile with recorded pins + compose + healthchecks (A2).
3. Settings + `.env.example` (A8/A9 constraints).
4. `db/connection.py` + Alembic wiring + migration 0001 (zero rows) with downgrade (A3, A12).
5. `SourceRegistryRecord` + synthetic contract fixtures (A6).
6. Hand-derive `expected_schema.json` and `expected_tree.json` from the cited doc sections and this plan (A4, A5); write the comparison tests/scripts.
7. Remaining tests: extension presence + functional checks (A2, A11), negative status, seed-absence checks (A13).
8. CI workflow with the full §4.8 step order; verify green on push (A8–A10, A12–A13 in CI).
9. Confirm, Validate, Test; produce evidence; create the immutable candidate commit.

**What must remain unchanged:** `docs/` (read-only authority); `.delivery/plans/` and `.delivery/reviews/`; no history rewrites; zero rows in `source_registry` anywhere in the candidate.

## 8. Dependencies and blockers

- Dependencies: none (first implementation task). Docker + uv on runner/workstation; no GPU, no external API, no credential.
- Blockers: none for TASK-001. FA-OPEN-020 gates TASK-006 (not this task). **Merge eligibility** (not implementation or review) additionally depends on GATE-SETUP (§11 / BOOTSTRAP_PLAN §9).

## 9. Stop conditions (stop and surface; do not guess)

1. Pinned AGE or pgvector releases cannot be built/loaded against Postgres 16 → STOP; surface pin options; do not switch Postgres major (doc 28).
2. Any doc-03 field proves irreconcilable with the §7.4 dual-identity model beyond what FA-OPEN-021 documents → STOP; record; do not invent.
3. Any acceptance criterion can only pass by weakening an oracle → STOP (oracle policy).
4. Any need for a module path, schema, event type, or component not defined in the docs folder → STOP; doc-23 anti-drift requires an ADR-style note WITH human (Salim) approval before implementation.
5. CI platform unusable for SHA-bound runs → STOP; surface to controller.

## 10. Test and evidence expectations

- Tests per §6 under `src/fath/tests/`; runnable via `make test` and in CI; no network access; fixed seeds where randomness exists; fixtures synthetic and non-persistent (§5).
- Evidence for review: CI run URL/output bound to the candidate SHA (labeled SHA-bound evidence); alembic cycle transcript; `pg_extension` listing; A4 schema-comparison output; A5 tree-check output; A12 zero-row outputs (both points); A13 outputs; scoped-scan and gitleaks outputs. Recorded under `.delivery/evidence/TASK-001/` by the implementer.

## 11. Completion conditions and gate sequencing (FATH-P2-004)

1. All acceptance criteria A1–A13 pass with recorded evidence; one immutable candidate commit; candidate SHA reported.
2. Independent implementation review (Sol seat) receives the exact SHA. On APPROVE the candidate state becomes **REVIEW_APPROVED — and stops there.**
3. **Merge eligibility is a separate, later state** and requires, per BOOTSTRAP_PLAN §9 GATE-SETUP and review policy §§36–46, ALL of: (a) branch protection on `main` verified ACTIVE (mechanical GitHub API evidence, not assumption — BUILD_STATE currently records it NOT_VERIFIED); (b) trusted exact-identity verification configured and run against this exact SHA with a recorded receipt (currently NOT_CONFIGURED); (c) BUILD_STATE updated to reflect the verified gate states. There is no review-plus-controller substitute for these gates; until they are verified active, this candidate — like every candidate — remains NOT merge-eligible.
4. No self-approval at any step.

## 12. Plan identity and review

- Plan path: `.delivery/plans/FATH-BOOTSTRAP/TASK-001_PLAN.md` (v3); SHA-256 recorded in the commit/handoff over this exact content.
- Reviewer: `plan-reviewer` (GPT-5.6 Sol, read-only, fresh context); outcomes APPROVE / REJECT / BLOCKED; **attempt 3 of max 3** — a rejection escalates to BLOCKED_FOR_SALIM.
