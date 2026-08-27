# TASK-001 — Repository Foundation: Scaffold, Environment, Database Baseline, Source Registry Schema, SHA-Bound CI Evidence

**Project:** FATH_AUTOPILOT · **Task ID:** TASK-001 · **Plan version:** v4 (fresh planning cycle under AMENDMENT-002)
**Author role:** TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max — runtime inherited from the Claude Fable 5 Thinking Max parent controller per control-plane model invariant)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (plan_review_attempt **1 of 3 — fresh review sequence** authorized by Escalation Policy §6: AMENDMENT-002 is a human-approved change in project authority that resolved the blocker (FATH-P3-001) which invalidated the previous attempt sequence; prior attempts 1–3 remain preserved in `.delivery/reviews/FATH-BOOTSTRAP/` and BUILD_STATE history) — NOT self-approved; authorizes no implementation until independent Sol review returns APPROVE.
**Branch when dispatched:** `task/TASK-001-repository-foundation` (cut from `main` after the controller merges the approved plan baseline).
**Lineage:** v2 per `REMEDIATION-1_ADJUDICATION.md`; v3 per `REMEDIATION-2_ADJUDICATION.md`; v4 per `V4_ADJUDICATION.md` (AMENDMENT-002 applied; FATH-P3-002/003/004/005 corrected).

This plan is subordinate to canonical `docs/` authority — precedence: `docs/34` AMENDMENT-002 and `docs/33` AMENDMENT-001 (human-approved amendments; 34 wins over everything earlier where conflicting; the two amendments do not conflict — different domains), then `docs/24` correction layer over 00–23, then the corpus — and to `BOOTSTRAP_PLAN.md` (v4) as reviewed. It creates no new requirements.

---

## 1. Objective

Create the minimal verifiable foundation on which every later bounded task builds: doc-16-conformant repository scaffold, reproducible uv-managed Python 3.11 environment, runnable local service stack (Postgres 16 with Apache AGE + pgvector, Redis 7), typed configuration loading, Alembic migration baseline, and the Source Registry **schema** per the AMENDMENT-002 source-identity model (structure only — zero rows, no seed artifacts; §5), with SHA-bound CI test evidence.

## 2. Authoritative references (read before implementing)

| Authority | Governs in this task |
|---|---|
| **docs/34 AMENDMENT-002** (sha256 `0edb5245…`) | Source-identity model (SPECIFIED, §§1–11): `source_registry` single canonical table, `source_id UUID PRIMARY KEY` immutable, `slug TEXT NOT NULL UNIQUE`, universal semantic rule, no `sources` table, no FK to `slug` absent human-approved ADR. §13: this task's independently derived expected-schema oracle (A4). §12 propagation map: `PROPAGATION_MAP.md` (binding planning material). |
| docs/33 AMENDMENT-001 | No Azure OpenAI SDK/endpoint/env in implementation/configuration (verifier item 2); no A100 assumption (item 1). This task introduces **no** LLM or GPU code. |
| docs/16 | **Canonical layout binding as written** (doc-23 anti-drift rule: deviations require an ADR WITH human approval — this task creates none). Modules: `safety/`, `budgets/`, `db/connection.py`, `db/migrations/`, `db/models/source_registry.py`, tests under `src/fath/tests/{fixtures,unit,integration}`. Root files per doc 16: `pyproject.toml`, `docker-compose.yml`, `README.md`. |
| docs/02 (as amended by 33) | Locked stack; single-Postgres decision; ADR supersession rule (human-approved per doc 23). |
| docs/22 §1 + §2 | Required extensions: uuid-ossp, vector, age; canonical table name `source_registry`. |
| docs/28 | Postgres 16, Redis 7 (running-version checks A2), Alembic migration policy and cycle test, secrets rules (.env local only). |
| docs/03 | SourceRegistryRecord field contract (fields, types, Pydantic defaults, numeric boundaries — A4/A6 oracle inputs), registry indices. Seed VALUES not established — §5, FA-OPEN-020. |
| docs/04 "Foreign keys"; docs/21 DDL | `raw_archive.source_id → source_registry.source_id`; `source_id UUID NOT NULL REFERENCES source_registry(source_id)` — surviving UUID contracts (AMENDMENT-002 §10) the schema must keep satisfiable. |
| docs/24 §1 | Source status enum + DB CHECK + DEFAULT 'candidate' — applies to `source_registry` per AMENDMENT-002 §1 (no `sources` table). Week-1 textual sets are slugs per §11. |
| docs/29, docs/30 | Compliance-table DDL superseded per AMENDMENT-002 §7 (UUID FKs → `source_registry(source_id)`, created in TASK-006); textual ids are slugs (§11); YAML keys on `slug:` (§8). Recorded as forward contracts — nothing from docs 29/30 is created in this task. |
| docs/23 | Week-1 done criterion "Source Registry table exists"; anti-drift rule (ADR + human approval). |
| Control plane: constitution §§9/19, review policy §§36–46, Oracle Policy §§5/7/10/11/37/48, SG-TR-007 | CI as SHA-bound evidence; candidates halt at REVIEW_APPROVED until the trusted gate is verified active (§11); oracle independence, boundary triplets, negative evidence, claim precision; uv; typing. |
| BOOTSTRAP_PLAN.md (v4) §§4, 6, 7.4, 9, 12 | Identity model (§7.4 → PROPAGATION_MAP.md), PROPOSED items (§4.4), dependency baseline (§6), CI + GATE-SETUP sequencing (§9). |

## 3. Requirements traced (from REQUIREMENTS_TRACEABILITY.json)

FA-REQ-W1-001 (registry **schema + indices** portion; seed data = TASK-006 gated on FA-OPEN-020), FA-REQ-W1-002 (status enum + CHECK — schema portion), FA-REQ-W1-018 (doc-16 layout), FA-REQ-W1-019 (PG16 + extensions; Redis 7), FA-REQ-W1-020 (Alembic cycle), FA-REQ-AM-003 (AMENDMENT-002 identity model + §13 oracle), FA-REQ-CP-001 (CI as SHA-bound evidence), FA-REQ-CP-002 (uv, typing), FA-REQ-CP-003 (governed workflow; halt at REVIEW_APPROVED pre-gate), FA-REQ-AM-001 (negative constraint: no Azure OpenAI artifact in implementation/configuration).

## 4. Scope (what must change)

1. **Repository scaffold — doc-16 canonical layout** for every path created (full anchored path oracle: §6.1/A5): `src/fath/__init__.py`; packages `config/`, `db/` (`connection.py`, `migrations/`, `models/`), `memory/`, `safety/`, `crawlers/`, `parsers/`, `extractors/`, `graph/`, `embeddings/`, `agents/`, `validators/`, `workflows/`, `events/`, `budgets/`, `ui/`, `api/`; tests under `src/fath/tests/{fixtures,unit,integration}`; root `pyproject.toml`, `docker-compose.yml`, `README.md`. Disclosed root-level additions (not module paths): `.gitignore`, `.env.example`, `alembic.ini`, `Makefile` (test/lint/typecheck targets only — PROPOSED), `docker/postgres/Dockerfile` (PROPOSED packaging, §4.4), `.github/workflows/ci.yml`, optional `.python-version` (content `3.11`). `docs/` untouched; `.delivery/` written ONLY under `.delivery/evidence/TASK-001/` (§10 — the single authorized exception, mechanically enforced by A16).
2. **Python environment:** `pyproject.toml` with `requires-python = ">=3.11,<3.12"` (Python 3.11 PROPOSED baseline, BOOTSTRAP_PLAN §4.4) + committed `uv.lock`. Direct dependencies limited to the §4.9 permitted contract. No FastAPI, LangGraph, Prefect, or any LLM/embedding dependency.
3. **Tooling config:** ruff (lint + format), mypy strict on `src/`, pytest config.
4. **Local service stack (PROPOSED packaging per BOOTSTRAP_PLAN §4.4):** `docker/postgres/Dockerfile` — Postgres 16 base pinned by digest; AGE and pgvector pinned to exact release tags recorded in the Dockerfile. `docker-compose.yml` with that image + pinned `redis:7` tag; named volumes; healthchecks.
5. **Typed configuration:** `src/fath/config/settings.py` (pydantic-settings) loading `DATABASE_URL`, `REDIS_URL`, `FATH_ENV` only; `.env.example` with placeholders for exactly those keys — no Azure OpenAI variable, no frontier-provider key (those enter with the Week-2 LLM-client task).
6. **Database baseline:** async SQLAlchemy engine/session factory in `db/connection.py`; Alembic with `script_location = src/fath/db/migrations`; **migration 0001**: enable the three extensions and create `source_registry` per the **AMENDMENT-002 identity model (SPECIFIED, docs/34 §§1–3)**:
   - `source_id UUID PRIMARY KEY` (immutable canonical identity; docs/34 §2; docs/03/04/21 surviving contracts). Server-side `DEFAULT uuid_generate_v4()` is PROPOSED (docs/34 §8 permits generated-or-assigned; uuid-ossp is the doc-22 §1 required extension); the A4 fixture pins whichever form the migration declares.
   - `slug TEXT NOT NULL UNIQUE` (docs/34 §3 — column name given by the amendment).
   - All other doc-03 fields with their types and nullability (per-column PG type mapping recorded with citations in the A4 fixture; mapping choices are DERIVED/PROPOSED per column there, e.g. `AnyUrl→TEXT`, `dict→JSONB`, `datetime→TIMESTAMPTZ`).
   - doc-24 §1 `status TEXT NOT NULL DEFAULT 'candidate'` + CHECK with exactly the 7 values — applied to `source_registry` per docs/34 §1.
   - DB-level column defaults are declared ONLY for `source_id` (PROPOSED above) and `status` (SPECIFIED docs/24 §1); every other doc-03 default is a Pydantic-layer default verified by A6. The A4 fixture asserts the ABSENCE of DB defaults on all other columns, so unpinned drift fails.
   - doc-03 source_registry indices (4: enabled, source_class, reliability_tier, independence_group). The two doc-03 `access_decisions` indices belong to the task that creates that table (TASK-006).
   - **The migration inserts zero rows.** Full downgrade implemented. **No `sources` table is created (docs/34 §1). No other table in this task** — the doc-29 compliance tables arrive with TASK-006 and will FK `source_id UUID REFERENCES source_registry(source_id)` per docs/34 §7 (forward contract, PROPAGATION_MAP PM-C3/C4; not created now).
7. **Pydantic contract:** `db/models/source_registry.py` — `SourceRegistryRecord` per the doc-03 field contract verbatim (`source_id: UUID` with uuid4 default) **plus** `slug: str` (SPECIFIED docs/34 §§3/5) and the doc-24 §1 `status` field (SPECIFIED). This module contains contract models only — no engine/session import (enforced by A13c import discipline).
8. **CI (SHA-bound evidence):** `.github/workflows/ci.yml` per BOOTSTRAP_PLAN §9, step order fixed in §4.10 below. **Classification: candidate-controlled test evidence bound to the exact SHA — never trusted verification. Trusted gates are NOT_CONFIGURED / branch protection NOT_VERIFIED (BUILD_STATE); this candidate halts at REVIEW_APPROVED and is NOT merge-eligible until the §11 gate sequencing completes.**
9. **Permitted dependency/environment contract (mechanically checked by A15):**
   - Permitted direct `[project.dependencies]`: `pydantic` (v2), `pydantic-settings`, `sqlalchemy` (2.x), `alembic`, `asyncpg`, `psycopg[binary]`, `redis`, `pyyaml`.
   - Permitted direct dev-dependencies: `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `types-pyyaml`, `testcontainers` (optional), `greenlet` (SQLAlchemy async runtime requirement, if the resolver does not pull it automatically).
   - Prohibited anywhere in `pyproject.toml` or `uv.lock` (name match): `fastapi`, `langgraph`, `prefect`, `openai`, `azure-openai`, any `azure-*` SDK, `anthropic`, `transformers`, `torch`, `sentence-transformers`, `vllm`, `unstructured`, `paddleocr`.
   - Python: `requires-python = ">=3.11,<3.12"`; CI asserts the running interpreter is 3.11.x (A14).
   - Declared-direct-dependency compliance is fully mechanical; transitive resolution is uv's (limitation stated per Oracle Policy §48 — the prohibited-name scan over `uv.lock` also covers transitives).
10. **CI step order (deterministic; every push/PR, bound to exact SHA):**
    1. checkout candidate SHA; assert `python --version` is 3.11.x (A14);
    2. `uv sync --frozen` (A1) + dependency-contract check (A15);
    3. `ruff check` + `ruff format --check`; `mypy src/` (A7);
    4. diff-boundary check (A16): candidate diff vs PR base touches nothing under `docs/` and nothing under `.delivery/` except `.delivery/evidence/TASK-001/**`;
    5. build pinned PG image; start postgres + redis services; running-version checks (A2);
    6. `alembic upgrade head` → **zero-row check (A12a)**;
    7. expected-schema comparison (A4) + functional extension checks (A11);
    8. `pytest` (unit + integration, against this database) → **post-test zero-row check (A12b)**;
    9. `alembic downgrade base` → `alembic upgrade head` → **zero-row check (A12c)** (doc-28 cycle = A3);
    10. expected-tree check (A5); seed-boundary checks: authoritative-literal scan (A13a), registry-write import/content discipline (A13b/A13c), fixture-content rules (A13d);
    11. scoped AMENDMENT-001 scan (A8); pinned gitleaks scan (A9).
    Fails on any error; no network calls in tests; fixed seeds where randomness exists.

## 5. Seed data — descoped AND negatively enforced (FATH-PR-001, FATH-P2-002, FATH-P3-003)

Authority establishes seed identities (as slugs per docs/34 §11) but not the required values (`base_url`, `reliability_tier` — mandatory doc-03 fields with no defaults — plus per-source rate limits and collection modes), and doc 29 requires human-approved onboarding checklists before activation. Seeds are therefore TASK-006 scope, gated on **FA-OPEN-020** (Salim-approved seed value table + Tier-0 checklists; dispatch without it is `BLOCKED_FOR_SALIM`).

For THIS candidate the boundary is mechanically enforced by checks that do not depend on any candidate-authored attestation (P3-003 correction):

- **A12 zero-seed state, three measurement points:** `SELECT COUNT(*) FROM source_registry` = 0 (a) after fresh `upgrade head` before tests, (b) **after the full pytest session against the same database** — this directly proves no test persisted a row (fixture non-persistence established by observation, not by marker), and (c) after the downgrade/upgrade cycle. Run as CI-level SQL independent of pytest.
- **A13a authoritative-literal scan:** over every tracked file in the candidate (`git ls-files`, minus `docs/**`, `.delivery/**`, and the single scan-list fixture below), a word-boundary case-insensitive scan for the authoritative source-identity literals must return zero hits: the 7 doc-24 §1 slugs (`qatar_open_data`, `world_bank`, `gdelt`, `al_meezan`, `qcb`, `qse`, `invest_qatar`), the doc-30 Tier-1/2 slugs, and the 16 doc-03 seed display names (e.g. "Qatar Open Data", "World Bank", "GCC-Stat"). This detects production seed identities **by value, in ANY file under ANY variable/file name** — closing the "neutral name inside a permitted file" path. The scan list itself is committed at `src/fath/tests/fixtures/authoritative_source_literals.json` (checker input, cited per doc section, the ONLY file exempt from A13a by exact path; it contains identities only — never base URLs, tiers, rate limits, or any FA-OPEN-020 value). The root `README.md` is inside the scan domain; its content must therefore avoid seed-source names (disclosed constraint).
- **A13b registry-write discipline (loader-behavior detection):** in this bounded candidate the ONLY code permitted to write to `source_registry` is migration 0001 (whose zero-insert property A12 proves). Mechanical enforcement: every tracked file under `src/` EXCLUDING `src/fath/tests/**` and `src/fath/db/migrations/**` must contain no reference to `source_registry` in combination with INSERT/write patterns (SQL `INSERT`, SQLAlchemy `insert(`, `.add(`, `executemany`, `COPY`) — scanned mechanically; AND
- **A13c import discipline:** database-access imports (`sqlalchemy`, `asyncpg`, `psycopg`, `alembic`) are permitted ONLY in `src/fath/db/connection.py`, `src/fath/db/migrations/**`, and `src/fath/tests/**`; every `src/fath/**/__init__.py` in this candidate must be empty or docstring-only; `src/fath/db/models/source_registry.py` imports pydantic/stdlib only. A loader "under a neutral name" cannot exist in this candidate without violating A13b or A13c: any effective loader needs both registry-write statements and DB access. Scans are mechanical (pattern-based); their residual limitation against deliberate obfuscation (e.g. encoded literals, dynamic imports) is stated per Oracle Policy §48 and is covered by the independent reviewer's inspection of the actual diff — the checks make the covert paths named by the reviewer mechanically detectable, and active obfuscation would itself be reviewable evidence of bad faith.
- **A13d fixture syntheticity (content rules, not attestation):** every file under `src/fath/tests/fixtures/` must (i) contain zero A13a authoritative literals, (ii) use only RFC-2606 reserved domains (`example.com/net/org`, `.test`, `.invalid`) in any URL value, and (iii) any `slug` value must match `^synthetic_[a-z0-9_]+$`. These are mechanical content rules that establish syntheticity independently of any marker. The v3 `SYNTHETIC-TEST-FIXTURE` marker remains as labeling hygiene but is **no longer load-bearing evidence** (it was self-attestation — FATH-P3-003).
- **No seed artifact paths:** no `src/fath/config/sources_seed.yaml` (in A5's PROHIBITED set for this candidate even though doc 16 lists it — it is TASK-006 scope), no `execution_rules.yaml`, no `*seed*` path under `src/` (`git ls-files` scan).

## 6. Acceptance criteria and oracles

### 6.1 A5 expected-tree oracle (anchored four-set manifest over the normalized Git tree — FATH-P2-003, FATH-P3-004)

**Scan domain (fixed):** the set `P` of file paths returned by `git ls-files` at the exact candidate SHA (the normalized tracked Git tree — file paths, forward slashes, repo-root-relative). Filesystem state is OUT of domain: `.venv`, caches, tool byproducts, and untracked files never enter `P` because they are not tracked; CI runs the check on a clean checkout of the candidate SHA. Two path prefixes are carved out of `P` before comparison: `docs/**` (read-only authority; A16 proves untouched) and `.delivery/**` (governed separately by A16: only `.delivery/evidence/TASK-001/**` may be ADDED by this candidate).

**Manifest:** the candidate commits `src/fath/tests/fixtures/expected_tree.json` — hand-derived from doc 16 and this plan (not generated from the working tree) — with four sets in which **every entry is a full anchored path or an anchored glob rooted at an authorized parent path. There are no unanchored patterns: a bare `__init__.py` or `*.py` pattern is prohibited in the manifest itself** (FATH-P3-004).

- **REQUIRED** (each entry cites doc 16 or this plan §4): `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `README.md`, `.github/workflows/ci.yml`, `docker/postgres/Dockerfile`, `alembic.ini`, `.gitignore`, `.env.example`, `src/fath/__init__.py`, for each module M ∈ {config, db, db/models, memory, safety, crawlers, parsers, extractors, graph, embeddings, agents, validators, workflows, events, budgets, ui, api}: `src/fath/<M>/__init__.py`, plus `src/fath/config/settings.py`, `src/fath/db/connection.py`, `src/fath/db/models/source_registry.py`, `src/fath/db/migrations/env.py`, exactly one `src/fath/db/migrations/versions/0001_*.py`, `src/fath/tests/fixtures/expected_schema.json`, `src/fath/tests/fixtures/expected_tree.json`, `src/fath/tests/fixtures/authoritative_source_literals.json`.
- **PERMITTED** (anchored; may exist): `Makefile`, `.python-version`, `src/fath/db/migrations/__init__.py`, `src/fath/db/migrations/versions/__init__.py`, `src/fath/db/migrations/script.py.mako`, `src/fath/tests/__init__.py`, `src/fath/tests/{fixtures,unit,integration}/__init__.py`, `src/fath/tests/unit/test_*.py`, `src/fath/tests/integration/test_*.py`, `src/fath/tests/fixtures/*.json`, `src/fath/tests/fixtures/*.yaml` (subject to A13d content rules), tool configs at root only: `ruff.toml`, `mypy.ini`, `pytest.ini`, `conftest.py` (root or under `src/fath/tests/`), `docker/postgres/*.sql`/`*.sh` init files.
- **DEFERRED** (canonical in doc 16 but NOT created by TASK-001; absence must not fail; presence outside PERMITTED fails): `frontend/**`, doc-16 per-module implementation files (e.g. `src/fath/crawlers/base.py`, `src/fath/safety/trust_boundary.py`, `src/fath/db/models/raw_archive.py`, …), `src/fath/config/sources_seed.yaml`, `src/fath/config/execution_rules.yaml`, `src/fath/safety/injection_patterns.yaml`, `docs/adr/**`, `golden/**`, `scripts/**`.
- **PROHIBITED** (must NOT exist; anchored): any path matching `src/fath/*/` whose first segment under `src/fath/` is not in the doc-16 module list above (this check is computed from `P`, so e.g. `rogue/__init__.py` or `src/fath/llm/__init__.py` fails), top-level `tests/**` or `migrations/**`, `src/fath/config/sources_seed.yaml`, any path matching `*seed*` under `src/`, any second migration version file.

**Check (mechanical):** (REQUIRED ⊆ P) ∧ (P ∩ PROHIBITED = ∅) ∧ (every p ∈ P after carve-outs is matched by REQUIRED ∪ PERMITTED). Because every REQUIRED/PERMITTED entry is anchored, any noncanonical path — including a stray `__init__.py` anywhere outside the enumerated parents — fails the third condition.

### 6.2 Criteria table

| # | Criterion | Oracle class / verification |
|---|---|---|
| A1 | `uv sync --frozen` succeeds from clean checkout; `uv.lock` committed | SPECIFIED (SG-TR-007); CI step |
| A2 | Services healthy AND **running versions verified**: `docker compose up -d` yields healthy postgres + redis; after migration `SELECT extname FROM pg_extension` ⊇ {uuid-ossp, vector, age}; `SELECT current_setting('server_version_num')::int` in [160000, 170000) (Postgres major 16); Redis `INFO server` reports `redis_version` major 7 | SPECIFIED (docs 22 §1, 28); integration test + CI (FATH-P3-002) |
| A3 | `alembic upgrade head` → `downgrade base` → `upgrade head` all succeed (doc-28 cycle) | SPECIFIED (doc 28); CI step |
| A4 | **Expected-schema oracle (docs/34 §13):** committed fixture `src/fath/tests/fixtures/expected_schema.json` — hand-derived from the cited doc sections (each column/constraint/default/index entry carries its citation: doc-03 fields; docs/34 §2 UUID `source_id` PK; docs/34 §3 `slug TEXT NOT NULL UNIQUE`; docs/24 §1 status + CHECK + DEFAULT 'candidate'; doc-03 indices), NOT generated from the SQLAlchemy/Pydantic code — compared mechanically against `information_schema`/`pg_catalog` after `upgrade head`. Must prove ALL of: (i) `source_registry.source_id` is UUID PRIMARY KEY; (ii) `slug` is TEXT NOT NULL with a UNIQUE constraint/index; (iii) **no table named `sources` exists** (negative query over `information_schema.tables`); (iv) **no FK in the database references `source_registry(slug)`** and every FK that references `source_registry` targets `source_id` (query over `pg_constraint`; vacuously satisfied in this candidate but mechanically executed — scope limitation stated: FK-target proof over later tables re-runs in each owning task per PROPAGATION_MAP); (v) **exact normalized DB defaults**: `pg_get_expr(adbin, adrelid)` output equals the pinned expected string for `source_id` and `status`, and **every other column has NO DB default** (adbin IS NULL); (vi) exact column types and nullability for every doc-03 field per the fixture's cited mapping; (vii) CHECK constraint value set is exactly the 7 doc-24 §1 statuses; (viii) the 4 doc-03 registry indices exist. Negative tests: INSERT with status `bogus` rejected (CHECK); INSERT with NULL slug rejected; duplicate slug rejected (UNIQUE); duplicate source_id rejected (PK) | SPECIFIED oracle (docs/34 §13 + docs 03/24) with per-column mapping citations; independent mechanical comparison (fixture independent of implementation code — Oracle Policy §7) (FATH-P3-002 defaults; AMENDMENT-002 §13) |
| A5 | **Expected-tree conformance** per §6.1: fixed `git ls-files` scan domain; anchored four-set manifest; no unanchored patterns | SPECIFIED base (doc 16) + task-scoped sets from this plan; mechanical script in CI (FATH-P3-004) |
| A6 | `SourceRegistryRecord` (doc-03 contract + `slug` + `status` per docs/34 §§3/5 and docs/24 §1) verified at the contract layer: (i) golden-positive fixture validates; (ii) golden-negatives rejected (missing required field, invalid enum, invalid URL, invalid status, missing slug); (iii) **every doc-03 field default asserted exactly** on an instance constructed without optional fields (e.g. `max_requests_per_minute == 30`, `max_pages_per_cycle == 200`, `max_bytes_per_cycle == 500_000_000`, `robots_status == UNKNOWN`, `auth_requirement == NONE`, `reliability_prior == 0.70`, `strategic_relevance_score == 0.50`, `enabled is True`, `update_frequency_hint == "unknown"`); (iv) **documented numeric boundaries tested at below/at/above** (Oracle Policy §10): `reliability_prior` and `strategic_relevance_score` accept 0 and 1, reject -0.001 and 1.001; `conint(ge=0)` fields accept 0, reject -1. Fixtures obey A13d content rules | SPECIFIED (doc-03 contract; docs/34 §§3/5; docs/24 §1); contract tests (FATH-P3-002 model defaults + boundaries) |
| A7 | ruff (lint+format) and mypy strict pass over `src/` | SPECIFIED (SG-TR-007); CI steps |
| A8 | **Scoped AMENDMENT-001 scan:** no `A100` / Azure OpenAI SDK/endpoint/deployment/env reference in: `src/`, `docker/`, `.github/`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `Makefile`, `alembic.ini`, `.env.example`. Exclusions: `docs/`, `.delivery/`, README doc citations | SPECIFIED (docs/33 verifier items 1–2, scoped per its own "implementation, configuration, or sizing" text); scripted CI scan |
| A9 | **Secret scan:** pinned-version gitleaks (PROPOSED tool) over the candidate tree passes; `.env` git-ignored (test); `.env.example` placeholders only | SPECIFIED intent (doc 28; SG-TR-006) + PROPOSED tooling; CI step + test |
| A10 | CI green on the exact candidate SHA, recorded as **SHA-bound test evidence** (never trusted acceptance; gates per §11) | Review policy §§36–46; CI run URL bound to SHA |
| A11 | **Functional extension checks:** create a table with `vector(1024)` column + HNSW index; create an AGE graph + run a minimal cypher query — both succeed | SPECIFIED (docs 22 §1, 02); integration tests |
| A12 | **Zero-seed state at three points (§5):** `source_registry` row count = 0 (a) after fresh `upgrade head`, (b) after the complete pytest session against the same DB (fixture non-persistence proven by observation), (c) after downgrade/upgrade cycle | SPECIFIED boundary (seeds = TASK-006/FA-OPEN-020); CI-level SQL checks independent of pytest (FATH-P3-003) |
| A13 | **No seed content or loader (§5):** (a) authoritative-literal scan zero hits over tracked files (scan-list fixture sole exact-path exemption); (b) registry-write pattern scan clean outside migrations/tests; (c) import discipline holds (DB imports only in connection.py/migrations/tests; `__init__.py` empty/docstring-only; models file pydantic-only); (d) fixture content rules: no authoritative literals, RFC-2606 domains only, `synthetic_` slug prefix; plus `git ls-files`: no `sources_seed.yaml`, no `*seed*` under `src/`. Marker demoted to non-evidentiary labeling. Residual obfuscation limitation stated per Oracle Policy §48; reviewer inspects actual diff | SPECIFIED boundary; mechanical value/content/pattern scans in CI (FATH-P3-003 — detects seed values/loader behavior under neutral names in permitted files, and establishes fixture syntheticity/non-persistence without candidate attestation) |
| A14 | **Python runtime:** CI asserts running interpreter is 3.11.x; `pyproject.toml` declares `requires-python = ">=3.11,<3.12"` (verified by test reading pyproject) | PROPOSED baseline (BOOTSTRAP_PLAN §4.4) mechanically enforced once this plan is approved; CI step + test (FATH-P3-002) |
| A15 | **Dependency/environment contract:** declared `[project.dependencies]` and dev group ⊆ the §4.9 permitted lists (exact-name comparison, mechanical); prohibited-name scan over `pyproject.toml` AND `uv.lock` finds none of the §4.9 prohibited names; `uv sync --frozen` proves lock integrity (A1) | SPECIFIED contract in this plan grounded in BOOTSTRAP_PLAN §6 dependency discipline + docs/33 (no Azure/LLM deps); scripted CI check (FATH-P3-002) |
| A16 | **Boundary conformance (diff-domain):** `git diff --name-only <PR base>..<candidate SHA>` shows (i) zero paths under `docs/`, (ii) every path under `.delivery/` matches `^\.delivery/evidence/TASK-001/` and is an addition (no modification/deletion of existing `.delivery/` files) | SPECIFIED task boundary (§4.1, §10 — FATH-P3-005); mechanical CI check |

## 7. Implementation sequence (bounded)

1. Scaffold per §4.1 + pyproject (3.11, §4.9 contract) + uv.lock + tooling configs (A1, A7, A14, A15).
2. Postgres Dockerfile with recorded pins + compose + healthchecks; version checks (A2).
3. Settings + `.env.example` (A8/A9 constraints).
4. `db/connection.py` + Alembic wiring + migration 0001 per §4.6 (zero rows, full downgrade) (A3, A12).
5. `SourceRegistryRecord` per §4.7 + synthetic contract fixtures per §5 rules (A6, A13d).
6. Hand-derive `expected_schema.json` (per-entry citations incl. docs/34 §§2–3, docs/24 §1), `expected_tree.json` (§6.1 anchored sets), and `authoritative_source_literals.json` (cited from docs/24 §1, docs/30, docs/03) (A4, A5, A13a).
7. Remaining tests: extension presence + functional checks (A2, A11), negative status/slug/PK tests (A4), boundary tests (A6).
8. CI workflow with the full §4.10 step order; verify green on push (A8–A16 in CI).
9. Confirm, Validate, Test; write evidence under `.delivery/evidence/TASK-001/` (§10); create the immutable candidate commit.

**What must remain unchanged:** `docs/` (read-only authority — A16); `.delivery/` except additions under `.delivery/evidence/TASK-001/` (A16); no history rewrites; zero rows in `source_registry` anywhere in the candidate (A12).

## 8. Dependencies and blockers

- Dependencies: none (first implementation task). Docker + uv on runner/workstation; no GPU, no external API, no credential.
- Blockers: none for TASK-001. FA-OPEN-020 gates TASK-006 (not this task). FA-OPEN-021 is RESOLVED by AMENDMENT-002 (docs/34). **Merge eligibility** (not implementation or review) additionally depends on GATE-SETUP (§11 / BOOTSTRAP_PLAN §9).

## 9. Stop conditions (stop and surface; do not guess)

1. Pinned AGE or pgvector releases cannot be built/loaded against Postgres 16 → STOP; surface pin options; do not switch Postgres major (doc 28).
2. Any doc-03 field proves irreconcilable with the docs/34 identity model → STOP; record; do not invent (docs/34 is human-approved authority; contradictions with it are escalation material, not design freedom).
3. Any acceptance criterion can only pass by weakening an oracle → STOP (Oracle Policy §§38–39).
4. Any need for a module path, schema element, event type, or component not defined in the docs folder (or a persisted FK that would target `source_registry(slug)`) → STOP; doc-23 anti-drift and docs/34 §6 require an ADR-style note WITH human (Salim) approval before implementation.
5. CI platform unusable for SHA-bound runs → STOP; surface to controller.

## 10. Test and evidence expectations (FATH-P3-005 resolution)

- Tests per §6 under `src/fath/tests/`; runnable via pytest in CI (and via the `Makefile` `test` target, which §4.1 discloses); no network access; fixed seeds where randomness exists; fixtures synthetic per §5/A13d.
- **Evidence writer and location (unambiguous):** the **implementer** writes all TASK-001 evidence, as new files only, under **`.delivery/evidence/TASK-001/`** — this is the single authorized `.delivery/` write for this task, included in the allowed-file scope (§4.1) and mechanically enforced by A16. No other `.delivery/` path (`plans/`, `reviews/`, `escalations/`, `audit/`) may be created, modified, or deleted by the candidate. Rationale: Role & Model Policy §8 assigns evidence creation to the implementer; Oracle Policy §46 requires a control-plane-defined location; this section defines it. The controller separately records durable state in the control-plane repository — never the candidate.
- Evidence for review: CI run URL/output bound to the candidate SHA (labeled SHA-bound evidence); alembic cycle transcript; `pg_extension` listing + version-check outputs (A2); A4 schema-comparison output; A5 tree-check output; A12 zero-row outputs (all three points); A13 scan outputs; A14/A15 outputs; A16 diff listing; scoped-scan and gitleaks outputs.

## 11. Completion conditions and gate sequencing (FATH-P2-004 — preserved verbatim from V3 in substance)

1. All acceptance criteria A1–A16 pass with recorded evidence; one immutable candidate commit; candidate SHA reported.
2. Independent implementation review (Sol seat) receives the exact SHA. On APPROVE the candidate state becomes **REVIEW_APPROVED — and stops there.**
3. **Merge eligibility is a separate, later state** and requires, per BOOTSTRAP_PLAN §9 GATE-SETUP and review policy §§36–46, ALL of: (a) branch protection on `main` verified ACTIVE (mechanical GitHub API evidence, not assumption — BUILD_STATE currently records it NOT_VERIFIED); (b) trusted exact-identity verification configured and run against this exact SHA with a recorded receipt (currently NOT_CONFIGURED); (c) BUILD_STATE updated to reflect the verified gate states. There is no review-plus-controller substitute for these gates; until they are verified active, this candidate — like every candidate — remains NOT merge-eligible.
4. No self-approval at any step.

## 12. Plan identity and review

- Plan path: `.delivery/plans/FATH-BOOTSTRAP/TASK-001_PLAN.md` (v4); SHA-256 recorded in the commit/handoff over this exact content.
- Reviewer: `plan-reviewer` (GPT-5.6 Sol, 1M, Max reasoning, fast OFF, read-only, fresh context); outcomes APPROVE / REJECT / BLOCKED; **attempt 1 of max 3 in the fresh AMENDMENT-002 review sequence** (Escalation Policy §6 counter reset recorded in BUILD_STATE with the prior sequence preserved).
