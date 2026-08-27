# FATH_AUTOPILOT — Project Bootstrap and Architecture Plan

**Plan ID:** FATH-BOOTSTRAP-PLAN v5 (review sequence 2 under AMENDMENT-002 — adjudications in `REMEDIATION-1_ADJUDICATION.md`, `REMEDIATION-2_ADJUDICATION.md`, `V4_ADJUDICATION.md`, `REMEDIATION-3_ADJUDICATION.md`)
**Project:** FATH_AUTOPILOT · **Repo:** baramiSG/Fath_Autopilot · **Baseline:** `ae5a4ea7db30d9ba243e29c98424702f5e0fb7a1` · **Amendment commits:** `234a24d9e012710352d35aa5b1314a6395614945` (docs/33), `af00923853e0234da403231258c822b949e9da00` (docs/34)
**Author role:** CHIEF_ARCHITECT · **Model:** Claude Fable 5 (1M, Thinking ON, Max — runtime inherited from the Claude Fable 5 Thinking Max parent controller per control-plane model invariant)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (review sequence 2, plan_review_attempt **2 of 3** — sequence 2 authorized by Escalation Policy §6 after human-approved AMENDMENT-002 resolved FATH-P3-001; seq2 attempt-1 REJECT record: `.delivery/reviews/FATH-BOOTSTRAP/plan-review-seq2-attempt-1.md`, findings FATH-V4-001..009 adjudicated and corrected in `REMEDIATION-3_ADJUDICATION.md`; the V1–V3 sequence remains preserved unchanged) — this plan is NOT self-approved and authorizes no implementation until independent Sol review returns APPROVE.

This plan is operational planning material, not new project authority. Canonical authority remains `docs/` — precedence: **`docs/34_AMENDMENT_002_SOURCE_IDENTITY.md` (AMENDMENT-002) and `docs/33_AMENDMENT_001_COMPUTE_AND_LLM_PROVIDER.md` (AMENDMENT-001), both HUMAN_APPROVED_AMENDMENT, at the top — doc 34 wins over every earlier document (including 33 and 24) where conflicting; the two amendments do not conflict (different domains)** — then doc 24 overriding docs 00–23 where they conflict for everything the amendments do not address. Classifications used: **SPECIFIED / DERIVED / PROPOSED / OPEN / BLOCKED** per control-plane constitution §6.

**AMENDMENT-001 (docs/33, sha256 `3ea00519a4e7b79adb2e1f60afcfd4c393906033c148fd254fb1d71e15c61589`, incorporated throughout):** no A100 GPUs; local GPU compute target is a **single NVIDIA RTX 5090 workstation**; **no Azure OpenAI** anywhere; agent reasoning uses **frontier LLM APIs via a provider-agnostic client with configurable model routing**; every earlier "GPT-5.4" mention reads as "the configured frontier reasoning model, accessed via API" with vision fallback staying fallback-only; security invariants unchanged.

**AMENDMENT-002 (docs/34, sha256 `0edb5245999e88382eab1c8a0f9679f45e60d3cd680903f3b56f3a3768dd9b99`, commit `af00923` committed alone, human-approved by Salim 2026-08-27, resolving FATH-BOOTSTRAP-ESCALATION-001 and FATH-P3-001; incorporated throughout):** `source_registry` is the single canonical source table (no `sources` table; `sources(id)` references superseded); `source_registry.source_id` is a **UUID PRIMARY KEY**, immutable canonical identity; `source_registry.slug` is **TEXT NOT NULL UNIQUE**, the human/config identifier, stable after activation except audited migration; universal semantic rule — `source_id` ALWAYS the UUID, `slug`/`source_slug` ALWAYS the readable identifier, `source_name` display-only; Pydantic models keep `source_id: UUID` and expose separate `source_slug: str` where needed; ALL persisted source FKs reference `source_registry(source_id)`, never `slug` absent an explicit human-approved ADR; doc-29 TEXT FK DDL superseded to UUID; YAML/catalogs key on `slug`; transport `source_id` strings are serialized UUIDs with `source_slug` exposed separately where useful; existing UUID contracts (docs 03/04/05/07/21) survive; textual identifiers (docs 24/29/30) survive as slugs. §12 mandates the full-corpus propagation sweep (delivered as `PROPAGATION_MAP.md`); §13 mandates the TASK-001 expected-schema oracle (delivered as TASK-001_PLAN A4).

---

## 1. Authority basis

Read in full at baseline commit: docs 00–32, docs/README.md (hashes recorded in `AUTHORITY_MANIFEST.json`), plus a sample of the combined file confirming it is a concatenation (REFERENCE_ONLY). Read in full at amendment commits: docs/33 AMENDMENT-001 (sha256 verified; commit `234a24d`) and docs/34 AMENDMENT-002 (sha256 verified byte-exact `0edb5245…`; commit `af00923`, committed alone). Control-plane governance read in full: constitution, role/model policy, oracle policy, review/acceptance policy, escalation policy, governance baseline, BUILD_STATE.yaml. Planning history read in full: all three Sol review records (attempts 1–3), both remediation adjudications, escalation FATH-BOOTSTRAP-ESCALATION-001 and its resolution, RUNTIME_AUDIT_NOTE_001. Additionally the complete corpus was mechanically swept for every source-identity token (method and results: `PROPAGATION_MAP.md`).

## 2. Build-readiness assessment

**Classification: `READY_WITH_NON_MATERIAL_OPEN_ITEMS`**

| Readiness input | Status | Evidence |
|---|---|---|
| Canonical authority documents | Present | 34 canonical files + AMENDMENT-001 (docs/33) + AMENDMENT-002 (docs/34), all hashed in manifest |
| Intended outcomes | Present | docs/00, 01 (incl. 10 six-week success criteria) |
| Requirements | Present | docs 03–16, 21–22, 25–30 (contract-level Pydantic/SQL/algorithms) |
| Acceptance criteria | Present | docs/23 Week-1 done criteria; docs/17 per-week verification; docs/27 quality gates; docs/32 readiness checklist; docs/34 §13 schema oracle |
| Business/domain rules | Present | docs/01, 03, 11, 12, 29, 30 |
| Architecture | Present and locked | docs/00, 02 (+ 16 layout, 22 DB detail), as amended by 33/34 |
| Source-identity model | **Present — RESOLVED** | docs/34 AMENDMENT-002 (human-approved). The FATH-P3-001 blocker and FA-OPEN-021 are closed |
| Data assumptions | Present | docs/03, 04, 29, 30 (public data only; five stores; provenance mandatory) |
| Integration assumptions | Present | docs/03, 09, 30 (source classes, access modes) |
| Security constraints | Present | docs/00, 05, 12, 19, 25, 26 (+ 24 corrections) |
| Environment constraints | Present | docs/33 (RTX 5090 workstation; frontier LLM APIs), 28 (services, secrets; Azure hosting options OPEN per 33) |
| Verification expectations | Present | docs/17, 23, 27, 31, 32, 34 §13 |
| Material unresolved decisions | None blocking bootstrap or TASK-001 | Open items FA-OPEN-001..014, 018, 019 are non-material now or have documented resolutions. FA-OPEN-021 is **RESOLVED_BY_AMENDMENT_002**. **FA-OPEN-020 (seed values + Tier-0 onboarding evidence) remains MATERIAL for TASK-006/007/008/014 dispatch** — Salim-owned; dispatching TASK-006 without the approved seed value table is `BLOCKED_FOR_SALIM` (see §12). |

Material missing authority (FATH-PR-001, still true and still governed): registry seed VALUES (base URLs, reliability tiers, per-source rate limits/collection modes) and doc-29 onboarding evidence for Tier-0 activations are not established by authority — AMENDMENT-002 resolves identity **semantics**, not these values. Handling unchanged: TASK-001 schema-only; TASK-006 gated on **FA-OPEN-020**. This does not block bootstrap approval or TASK-001.

## 3. Material contradictions found and their classification

Full register: `REQUIREMENTS_TRACEABILITY.json → open_items`. Summary:

| Item | Conflict | Classification |
|---|---|---|
| A100 / Azure OpenAI (former locked stack) | docs 00/02/18/21/README "Azure OpenAI GPT-5.4 only", "8×A100 VM", "no extra frontier LLMs" vs owner instruction | **RESOLVED_BY_AMENDMENT_001 (SPECIFIED)** — RTX 5090 workstation; provider-agnostic frontier-LLM API client; interpretation rules for all GPT-5.4 mentions |
| FA-OPEN-021 | Source identity: docs 03/04/05/07/21 UUID storage contracts vs docs 24/29/30/06 textual identifiers; doc-29 `sources(id)` parent table mismatch | **RESOLVED_BY_AMENDMENT_002 (SPECIFIED)** — docs/34 §§1–11: UUID `source_id` PK + `slug TEXT NOT NULL UNIQUE` on the single canonical `source_registry`; all persisted source FKs → `source_registry(source_id)`; transport `source_id` strings = serialized UUIDs; YAML keys on `slug`. Full per-surface mapping: `PROPAGATION_MAP.md` |
| FA-OPEN-016 | doc 04 global `UNIQUE(content_hash_sha256)` vs doc 24 §2 provenance-preserving inserts | **RESOLVED_BY_24** — no global hash uniqueness; session duplicate guard index instead |
| FA-OPEN-017 | doc 04 FactLifecycle vs doc 24 §3 FactStatus | **RESOLVED_BY_24** — FactStatus + transition map govern |
| FA-OPEN-015 | doc 23 Week-1 Al Meezan collector criterion vs doc 24 §1 / doc 18 | **RESOLVED_BY_24** — registry definition only; no Week-1 collection |
| FA-OPEN-001 | Canvas registry delta (24 §4 vs 07) | **OPEN** (non-material until Week 3/6; human-approved ADR then) |
| FA-OPEN-002 | grounding similarity 0.72 (10, 11) vs 0.68 (21) | **OPEN** (material Week 5; ADR then) |
| FA-OPEN-003 | embedding namespace lists (10 vs 21) | **OPEN** (material Week 2; ADR then) |
| FA-OPEN-004 | module paths (31 vs 16) | **OPEN** (material Week 2; human-approved ADR per doc-23 anti-drift rule) |
| FA-OPEN-005/013 | migration numbering; Week-1 minimal facts vs Week-2 full store | **OPEN→DERIVED** sequencing (illustrative numbering; minimal-then-full) |
| FA-OPEN-006/007/008 | table naming, event casing, blob field naming | **OPEN→DERIVED** naming resolutions (§7); the `sources`-vs-`source_registry` component of FA-OPEN-006 is now settled by docs/34 §1 (SPECIFIED) |
| FA-OPEN-020 | seed record values (base_url, reliability_tier, rate limits, collection modes) and Tier-0 onboarding evidence not established by docs 03/29/30 | **OPEN — MATERIAL for TASK-006+**: Salim-approved seed value table + onboarding checklists required; no invented values permitted |
| FA-OPEN-009..012 | frontier-LLM API keys, RTX 5090 workstation connection + sizing re-derivation, production auth provider (flagged OPEN by 33), Comtrade key | **OPEN** provisioning (future weeks; interim paths specified) |
| FA-OPEN-018/019 | mandatory frontier provider designation; production secrets/object-store hosting | **OPEN** per AMENDMENT-001 (reserved to Salim; config-level routing and self-hosted interim paths keep all weeks unblocked) |

No `BLOCKED` and no `BLOCKED_FOR_SALIM` items exist for the bootstrap or TASK-001 scope.

## 4. Architecture decisions by classification

### 4.1 SPECIFIED (locked by docs/00 §Locked technology decisions and docs/02, as amended by AMENDMENTS 001/002; not renegotiable without ADR, and never against an amendment)

| Decision | Source |
|---|---|
| **Source identity: `source_registry` single canonical source table (no `sources` table); `source_id UUID PRIMARY KEY` immutable; `slug TEXT NOT NULL UNIQUE` human/config identifier; `source_name` display-only; ALL persisted source FKs → `source_registry(source_id)` (never slug absent human-approved ADR); transport `source_id` strings = serialized UUIDs with separate `source_slug` where useful; YAML/catalogs key on `slug`; doc-29 TEXT FK DDL superseded to UUID** | **AMENDMENT-002 (docs/34 §§1–11)**; propagation: `PROPAGATION_MAP.md` (binding on all task plans) |
| LangGraph workflows; Prefect 3 scheduler | 00, 02, 13 |
| Postgres single operational DB; Apache AGE in-Postgres graph; pgvector HNSW | 00, 02, 22 |
| Postgres major version 16 | 28 (production services) |
| BGE-M3 embeddings, 1024-dim | 00, 02, 10, 21 |
| Redis Streams event bus + FastAPI SSE; Redis for budget counters only (not source of truth) | 00, 02, 06, 14 |
| FastAPI backend; Next.js + React + TypeScript frontend | 00, 02, 16 |
| Controlled generative UI: JSON specs only, approved components, dual validation | 00, 07, 24 §4 |
| Agent reasoning via frontier LLM APIs through a provider-agnostic client with configurable model routing; NO Azure OpenAI SDK/endpoint/deployment/env anywhere; no provider hard-coded as the only path; all calls budget/rate/breaker-governed and trust-boundary-mediated | **AMENDMENT-001 (docs/33 Corrections 3–4, rules 3–5, verifier items 2–3, 5)** |
| Local GPU compute target: single NVIDIA RTX 5090 workstation for BGE-M3 embeddings, PaddleOCR, Nougat, optional local reranker, simulation, batch; no A100 assumption anywhere; A100-derived concurrency/batch assumptions re-derived per owning task | **AMENDMENT-001 (docs/33 Corrections 1–2, verifier items 1, 4)** |
| PDF chain: unstructured.io → PaddleOCR → Camelot → Nougat → configured frontier vision-capable model via API, fallback only | 00, 02, 09 (as read under AMENDMENT-001 rule 2) |
| Deterministic template simulation first; sandbox no-network | 02, 26, 24 §10 |
| Browser automation disabled v1; external actions blocked by default | 00, 02 |
| Repository layout and module boundaries | 16 |
| Hash-chained append-only Postgres audit log; in-transaction audit writes | 15, 24 §8 |
| Five memory stores with separation and provenance rules | 00, 04 |
| Alembic migrations with upgrade/downgrade discipline | 28 |
| MinIO (dev) object storage for raw artifacts; production object-store hosting OPEN per AMENDMENT-001 (self-hosted MinIO interim operative) | 28; 33 (Flagged OPEN) |
| Secrets: .env local only; never in logs/audit/events; production secrets hosting OPEN per AMENDMENT-001 | 28; 33 (Flagged OPEN) |
| Week-1 active sources exactly `qatar_open_data`, `world_bank`, `gdelt` (slugs per docs/34 §11) | 24 §1, 23, 30; 34 §11 |

### 4.2 SPECIFIED by control-plane governance (not by project docs)

| Decision | Source |
|---|---|
| uv for Python dependency/environment management; type hints on public functions; no bare except | SG-TR-007 (control plane). Project docs specify pyproject.toml (16) and name no package manager — no conflict. |
| Independent review binds to exact candidate SHA; task branches + PRs to main; no self-approval | Control-plane constitution §8, review policy §16–21 |
| Deterministic CI producing **SHA-bound test evidence** for every candidate. NOT trusted verification: the trusted gate (externally protected CI + branch protection + receipts) is **NOT_CONFIGURED** / **NOT_VERIFIED** per BUILD_STATE, and candidate-controlled Actions cannot be a trusted mechanism (review policy §§36–46). GATE-SETUP (§9) is REQUIRED BEFORE FIRST MERGE; until verified, candidates halt at REVIEW_APPROVED. | Constitution §§9/19; review policy §§36–46 (repo currently has NO CI — see §9) |

### 4.3 DERIVED (logically necessary; derivation stated)

| Decision | Derivation |
|---|---|
| Postgres event outbox table + Redis Streams transport coexist | Doc 06 rejects a Postgres event BUS; docs 22/23 require durable event_outbox storage; reconciled as transport vs durable record (FA-REQ-W1-009). |
| The provider-agnostic LLM client is a Week-2 prerequisite task, built before any extractor task or any model-driven UI-spec generation | AMENDMENT-001 mandates the abstraction for all agent reasoning; doc-31 extractors and the doc-07/18 model-produced UI specs are its consumers; sequencing it first avoids per-consumer provider coupling. Module path resolved by Week-2 human-approved ADR (doc-23 anti-drift; FA-OPEN-004). |
| Migration sequencing: numbering assigned in creation order; first facts-creating migration carries full FactStatus | Doc 24 §3 + doc 23 ("first fact migration"); doc-31 filenames treated as illustrative (FA-OPEN-005). |
| Week 1 minimal Fact Store slice; Week 2 full store | Doc 23 done criteria vs doc 17 Week-2 "full implementation" (FA-OPEN-013). |
| Frontend scaffolding deferred to the Canvas frontend task (not TASK-001) | Doc-16 layout includes frontend/, but no Week-1 criterion tests frontend existence before Canvas v0; deferring keeps candidates bounded and reviewable (constitution §7). |
| Specific DERIVED applications of the docs/34 rules to surfaces the amendment does not name verbatim (belief-calibration dict keys, per-source Redis budget `scope_id`, AGE `Source` node properties, doc-25 `target_id` when the target is a source) | Each derivation stated per-surface in `PROPAGATION_MAP.md` (PM-D15, PM-N1, PM-N2, PM-F2); binding on owning tasks; reviewer sees each derivation explicitly. |

*(The V3 dual-identifier row formerly in this table is superseded: the identity model is now SPECIFIED by AMENDMENT-002 — see §4.1 and §7.4.)*

### 4.4 PROPOSED (reversible engineering choices — reviewer may reject without touching authority)

| Proposal | Rationale |
|---|---|
| **Custom Postgres image bundling PG16 + AGE + pgvector** for docker-compose and CI (reclassified from DERIVED per FATH-PR-005) | Docs 02/22/28 require one PG16 instance with both extensions but do NOT require this packaging method (alternatives exist: init scripts on a pgvector base, prebuilt third-party images). PROPOSED: pinned Dockerfile with base image pinned by digest and AGE + pgvector pinned to exact release tags recorded in the Dockerfile; functional extension checks (vector column + HNSW index; AGE graph + cypher call) required in tests (TASK-001 A11). Running-version checks per TASK-001 A2. Reversible. |
| **Week-1 runs with zero reasoning-model calls** (reclassified from DERIVED per FATH-PR-004) | NOT necessary: doc 14 permits 200 LLM calls in daily_ingestion, and docs 07/18 define model-produced UI specs with one-retry semantics. PROPOSED sequencing because FA-OPEN-009 credentials are unprovisioned and AMENDMENT-001 requires the provider-agnostic client before any model call. Defined behavior: Week-1 Canvas v0 generates UI specs via a deterministic event→component producer behind a spec-producer interface; the doc-07 validate → reject → retry-once → fallback pipeline is fully implemented and fixture-tested in Week 1; the model-driven producer plugs into the same interface in Week 2 behind the LLM client. Week-1 extraction uses `deterministic_api` extraction (doc 04 enum) for the minimal fact criterion. If the reviewer rejects this proposal, the alternative is scheduling the LLM-client task inside Week 1, which places Week 1 behind FA-OPEN-009 (Salim credentials). |
| Python 3.11 as interpreter baseline | Not specified anywhere in docs. 3.11 chosen for widest wheel compatibility with the locked ML tooling arriving in Weeks 2–4 (unstructured.io, PaddleOCR, Nougat, vLLM ecosystems historically lag newest CPython). Mechanically enforced by TASK-001 A14 once this plan is approved. Reversible via pyproject change + ADR note. |
| Server-side `DEFAULT uuid_generate_v4()` on `source_registry.source_id` | docs/34 §8 permits UUID "generated or assigned" at record creation; uuid-ossp is the doc-22 §1 required extension; a server-side default is one valid mechanism (app-side Pydantic uuid4 default also exists per doc 03). Pinned exactly in the TASK-001 A4 fixture. Reversible. |
| GitHub Actions as the CI platform | Repo is GitHub-hosted; Actions gives SHA-bound required checks usable for branch protection and future trusted receipts. Reversible. |
| Dev tooling: ruff (lint+format) + mypy (strict on src/) + pytest | Enforces SG-TR-007 mechanically; doc 16 requires typed functions. Reversible. |
| SQLAlchemy 2.x + asyncpg as DB access layer under the memory services | Doc 24 §8 shows SQLAlchemy session patterns (evidence the corpus assumes SQLAlchemy); async matches FastAPI. Reversible. |
| gitleaks (pinned version) as the secret-scanning tool in CI | No project doc names a scanner; doc 28 + SG-TR-006 require the outcome. Reversible (FATH-PR-003 A9 oracle). |
| Canonical physical table names per §7 | See §7; reviewer confirms. |

## 5. Repository scaffolding plan (what the foundation must create)

Target-state tree: `PROJECT_MAP.md §2` (doc 16 + control-plane additions `.delivery/`, `.github/workflows/`, plus `golden/`, `scripts/`, `Makefile` required by docs 27/28/31). Scaffolding is delivered incrementally by bounded tasks (ROADMAP.md); TASK-001 creates the package skeleton, config, DB foundation, and CI (TASK-001_PLAN.md v5).

## 6. Environment and dependency baseline

- **Runtime services (local/dev):** docker-compose with `postgres` (custom PG16+AGE+pgvector image, pinned — PROPOSED §4.4), `redis:7` (pinned). MinIO added by the Raw-Archive task; Prefect/vLLM/sandbox services added when their tasks arrive. (SPECIFIED set; incremental introduction is DERIVED from bounded-task discipline.) Running-version verification (PG major 16; Redis major 7) is a TASK-001 acceptance criterion (A2).
- **Python:** uv-managed `pyproject.toml` (`requires-python = ">=3.11,<3.12"` — PROPOSED baseline) + committed `uv.lock` whose freshness is proven by `uv lock --check` (official uv semantics; `--frozen` does not check freshness — FATH-V4-004). TASK-001 dependency baseline is minimal and closed as a **three-set contract** (REQUIRED / OPTIONAL / PROHIBITED with positive completeness — exact lists: TASK-001_PLAN §4.9, mechanically checked by A15): REQUIRED pydantic v2, pydantic-settings, SQLAlchemy 2, alembic, asyncpg, redis, PyYAML (dev: pytest, pytest-asyncio, ruff, mypy, types-pyyaml); OPTIONAL psycopg[binary], testcontainers, greenlet. Each later dependency (fastapi, langgraph, prefect, unstructured, …) enters ONLY with the task that uses it, with the doc that specifies it cited in that task's plan (dependency discipline).
- **Secrets:** `.env.example` with placeholder keys for exactly `DATABASE_URL`, `REDIS_URL`, `FATH_ENV` — **excluding every Azure OpenAI variable** (AMENDMENT-001 verifier item 2); frontier-LLM API key names enter with the Week-2 LLM-client task as configuration; real `.env` git-ignored; no secret in any artifact.

## 7. Naming and schema resolutions

1. **Physical table names (DERIVED, reviewer to confirm — FA-OPEN-006):** `source_registry`, `access_decisions`, `raw_archive` (+ doc-22 names for tables only doc 22 defines). Basis: docs 03/04 define these names including FK references (`raw_archive.access_decision_id → access_decisions.decision_id`); doc 24's `sources`/`raw_archive_records` snippets state semantic corrections (status column, duplicate guard), not renames. **The `sources`-vs-`source_registry` component is now SPECIFIED: docs/34 §1 states there is no `sources` table and maps `sources(id)` references to `source_registry(source_id)`.** Doc-24 semantics are applied verbatim to the canonical names.
2. **Event types (DERIVED):** doc-06 catalog CamelCase names are canonical; snake_case mentions in docs 05/09/12 map to their catalog equivalents.
3. **UntrustedBlob fields (DERIVED):** doc-05 field contract governs; doc-24 §7 immutability (`model_copy`), delimiter escaping, and a truncation flag are binding additions.
4. **Source identity model — SPECIFIED by AMENDMENT-002 (docs/34), replacing the V3 DERIVED/PROPOSED reconciliation and closing FA-OPEN-021 and FATH-P3-001:**
   - `source_registry` is the single canonical source table; **no `sources` table** (§1).
   - `source_id UUID PRIMARY KEY`, immutable canonical internal identity (§2). All internal relational FKs named `source_id` reference `source_registry(source_id)` (§2, §6).
   - `slug TEXT NOT NULL UNIQUE` — the human-readable/config identifier (§3); the docs-24 §1 / 29 / 30 textual identifiers survive as slug values (§11).
   - Universal semantic rule (§4): `source_id` = UUID always; `slug`/`source_slug` = readable id; `source_name` = display only; no contract may use `source_id` to carry a slug.
   - Pydantic/domain models retain `source_id: UUID`; readable ids travel as separate `source_slug: str` (§5).
   - ALL persisted source FKs → `source_registry(source_id)` — Access Guard decisions, Raw Archive, onboarding checklists, terms snapshots, crawler records, retrieval records, provenance records, poisoning/integrity records, memory-store references, audit/evidence records, and every other persisted source FK (§6). FKs to `slug` are prohibited absent an explicit human-approved ADR (§6) — a stop condition in every task plan.
   - Doc-29 DDL corrected per §7: `source_id TEXT ... REFERENCES sources(id)` → `source_id UUID ... REFERENCES source_registry(source_id)`.
   - YAML/catalog definitions key on `slug:`; the UUID is generated/assigned at registry-record creation (§8). The doc-30 template's `source_id:` key is superseded accordingly.
   - Transport (§9): event/API/Redis/UI `source_id` strings are serialized UUIDs — they do NOT become slugs; payloads may carry `source_id` + `source_slug` + `source_name` with distinct semantics. This replaces — and reverses — the V3 rule that event/UI `source_id: str` carries the slug (the FATH-P3-001 defect).
   - Surviving contracts (§§10–11): every UUID source contract in docs 03/04/05/07/21 stands verbatim; every textual identifier in docs 24/29/30 stands with slug semantics.
   - **Complete per-surface propagation (docs/34 §12): `PROPAGATION_MAP.md`** — **84 mapped rows** (count corrected per FATH-V4-009; provenance/graph surfaces added per FATH-V4-007: graph-edge/node `source_refs` in docs 27/31/32, doc-15 UI-card "source object IDs", audit event types, golden-directory naming, doc-32 checklist rows) across tables, columns, FKs, Pydantic models, event payloads, API/UI/crawler/retrieval/provenance/poisoning/onboarding contracts, YAML/catalogs, and supplementary representations (Redis budget keys, metrics/log fields, CLI args, AGE node properties, belief-calibration dicts), each with citation and classification; genuinely ambiguous semantics recorded as explicit OPEN items (FA-OPEN-022, FA-OPEN-023) rather than left implicit. Binding on all task plans.
   - **Schema oracle (docs/34 §13): TASK-001_PLAN A4** — expected-schema fixture whose complete content (table set, 33 columns with exact PG types/nullability, normalized defaults, named constraints incl. numeric-boundary CHECKs, index set, immutability trigger, zero-FK assertion) is **pre-bound in TASK-001_PLAN §6.0** (FATH-V4-002): the implementer transcribes, never invents. `source_id` immutability is mechanically enforced by a DB trigger with a negative test (FATH-V4-001); slug post-activation stability enforcement is assigned to TASK-006 (the task introducing activation) as a binding acceptance obligation.

If the plan reviewer rejects any DERIVED reading above, the correction is a plan remediation, not an implementation-time improvisation.

## 8. Security and data boundaries (plan-level)

- **Trust boundary:** all external content wrapped as UntrustedBlob with sanitization, injection scoring, quarantine ≥ 0.85, delimiter escaping; no raw web text as instructions (docs 05, 24 §7; verified by fixture tests before any continuous crawling — doc 27 security gates).
- **Module boundaries as security controls:** crawlers cannot import the LLM router; extractors cannot write hypotheses; UI cannot modify analysis records (docs 08, 16 — enforced by architecture tests).
- **Action restriction:** no external-action code paths; approvals RBAC-enforced in backend when introduced (docs 00, 25, 24 §12); RBAC required before Week-5 publication/quarantine flows (doc 25 build order).
- **Data:** public sources only; PII rules per doc 29; no LMIS/QNWIS/ministry-private data anywhere.
- **Secrets:** never committed, never logged, never in prompts or artifacts (doc 28 + control-plane §17). The spec corpus itself is Salim-authored, non-client material — permitted in this seat.
- **Sandbox (Week 4):** no-network container, blocked imports, resource caps (doc 26).

## 9. CI plan — SHA-bound test evidence (trusted gate NOT_CONFIGURED)

**Classification (FATH-PR-006, corrected per FATH-P2-004; unchanged in V4):** the TASK-001 CI is **candidate-controlled, SHA-bound test evidence**. It is NOT trusted verification and is never described as a trusted gate. Current durable state (BUILD_STATE.yaml): `trusted_ci_verification: NOT_CONFIGURED`, `formal_review_receipt: NOT_CONFIGURED`, `branch_protection: NOT_VERIFIED`, merge NOT_ELIGIBLE. **There is no substitute path to merge eligibility** — no review-plus-controller process, no exception (constitution §§9/19 fail-closed; review policy §§36–46).

**GATE-SETUP — required sequencing BEFORE any candidate (including TASK-001) becomes merge-eligible:**
1. **Branch protection on `main`** — configured by **Salim** (repo admin; only human authority can perform repository-settings actions): require PRs, require the CI status check on the exact merge candidate, prohibit force pushes, enforce including admins. *Verification that it is ACTIVE:* mechanical GitHub API evidence (e.g. `gh api repos/<owner>/<repo>/branches/main/protection` output) recorded under `.delivery/evidence/GATE-SETUP/`; no protection claim is made anywhere until this evidence exists.
2. **Trusted exact-identity verification** — the protected, non-candidate-controlled CI run bound to the exact candidate SHA, with a recorded receipt (run URL + SHA + immutable log) per review policy §§36–46. Configured after (1); verified by receipt evidence.
3. **BUILD_STATE update** — the controller records the verified gate states (with the evidence paths) before any merge-eligibility declaration.

Until all three are verified active, every candidate — TASK-001 included — stops at **REVIEW_APPROVED** and is **NOT merge-eligible**. This sequencing adds no weakening: it forbids exactly the merges the prior wording would have permitted.

**Platform (PROPOSED):** GitHub Actions in `.github/workflows/ci.yml`, created by TASK-001.

**Pipeline (identical for push and PR events, bound to exact SHA):** the deterministic step order is fixed in TASK-001_PLAN §4.10 (runtime-version checks, **`uv lock --check` then `uv sync --locked`** — `--frozen` does not verify lock freshness per official uv docs (FATH-V4-004) — + three-set dependency contract, lint/type, **governed-base diff-boundary check** (`git diff --name-status --no-renames` against the controller-recorded task base SHA, event-independent — FATH-V4-005), migration cycle with three zero-row measurement points, expected-schema and expected-tree oracles, seed-boundary scans incl. migration-DML scan, scoped AMENDMENT-001 scan, pinned gitleaks).

**Determinism rules:** pinned image digests/versions, `uv.lock` proven current (`uv lock --check`) and synced `--locked`, no network calls in tests (connectors tested against recorded/golden fixtures — doc 27 pattern), fixed random seeds where randomness exists (oracle policy §27).

## 10. Test strategy (evidentiary, per oracle policy)

- **Layer 1 — contract tests (SPECIFIED oracles):** every Pydantic model validated with golden-positive and golden-negative fixtures derived from doc contracts (invalid enum, out-of-range confloat, missing provenance, unknown fields where forbidden), plus boundary triplets (below/at/above) for documented numeric bounds.
- **Layer 2 — behavior tests (SPECIFIED oracles):** the doc-listed minimum tests are mandatory floors: doc 05 (6 trust-boundary tests + spoofing test from 24 §7), doc 06 (7 event-bus tests), doc 09 (6 crawler tests), doc 24 verifier checklist items, doc 23 done criteria, docs/34 verifier checklist items 1–5.
- **Layer 3 — integration (SPECIFIED):** migration cycles, extension presence + running versions, end-to-end Week-1 heartbeat smoke (TASK-014) with recorded evidence.
- **Layer 4 — golden evaluation (REFERENCE oracles, Week 2+):** `golden/` datasets with provenance per doc 27; `make eval` producing EvalReport bound to git commit; thresholds per doc 27 tables. Golden files change only via oracle-change review (oracle policy §13).
- **Layer 5 — security regression (SPECIFIED):** injection fixtures, delimiter spoofing, boundary-import tests, RBAC fixtures (Week 5), sandbox no-network tests (Week 4) — the doc-27 security gates run before any continuous autonomous operation.
- **Negative evidence:** for consequential logic, tests must fail when a sign/threshold/field is wrong (oracle policy §11) — e.g. audit chain tamper detection, wrong-hash rejection, budget breach continuing would fail, `sources`-table presence, slug-targeting FK, or a `source_id` UPDATE slipping past the immutability trigger would fail the A4 oracle.
- Tests never weaken oracles to pass; conflicts stop work and surface (oracle policy §38).

### 10.6 Evidence retention model (project-wide convention — FATH-V4-006)

This model governs **every** task from TASK-001 onward and resolves the evidence-sequencing paradox (post-commit CI output cannot exist pre-commit; committing it afterward would change the candidate SHA):

1. **Pre-candidate committed evidence** — everything derivable from the candidate's tree content alone, produced by the implementer running the checks locally against the exact content that becomes the candidate: test/scan/oracle transcripts, migration-cycle transcripts, tool versions, the recorded base SHA. Committed **inside** the candidate under `.delivery/evidence/TASK-<ID>/` (new files only). These artifacts are content-bound; they never reference the candidate SHA, because it does not exist yet.
2. **Post-candidate external evidence** — everything bound to the candidate SHA after it exists: the CI run URL and results for that exact SHA, independent-review records, trusted-gate receipts. **Never committed into the candidate.** Retained by the controller in control-plane `BUILD_STATE.yaml` (SHA → CI URL/result/receipt entries) and in `.delivery/reviews/**` records committed in later commits on the plan/main lineage. Such later commits never claim membership in the reviewed candidate; the reviewed identity is always the immutable candidate SHA.
3. Any acceptance criterion that consumes SHA-bound CI output (e.g. TASK-001 A10) is verified by the reviewer/controller against the post-candidate external record — not against files inside the candidate.
4. No evidence is ever back-committed into a reviewed candidate, and no candidate SHA is ever recomputed to absorb evidence.

## 11. Governed Git workflow for this project

- `main`: target branch, PR-only merges after gates. Branch protection is currently **NOT_VERIFIED** (BUILD_STATE) — it must be configured by Salim and mechanically verified per §9 GATE-SETUP before any merge-eligibility declaration; no candidate merges before that.
- `plan/*`: planning artifacts (this branch: `plan/bootstrap-and-task-001`).
- `task/TASK-XXX-<slug>`: one branch per bounded task, cut from current `main` (TASK-001 branches from the merged plan baseline once this plan is approved; the controller manages merge of the plan branch).
- Implementer produces an immutable candidate commit; review binds to that exact SHA; any change → new candidate → fresh review (review policy §16–21, escalation ladder per escalation policy).
- Commits: imperative, task-scoped messages referencing the task ID; no history rewrites on shared branches; merge only when merge-eligibility inputs recorded in BUILD_STATE are satisfied.
- `.delivery/` in this repo holds plan/evidence artifacts; durable workflow state lives in the control-plane BUILD_STATE.yaml (single source of truth for counters/states). Task candidates write `.delivery/` ONLY at their authorized evidence path (TASK-001: `.delivery/evidence/TASK-001/` — TASK-001_PLAN §10/A16).

## 12. Open items and blockers

- **Blockers:** none for bootstrap or TASK-001.
- **Resolved by amendment:** FA-OPEN-021 (source identity) — **RESOLVED_BY_AMENDMENT_002** (docs/34; propagation in `PROPAGATION_MAP.md`). The Azure/A100 stack contradiction — RESOLVED_BY_AMENDMENT_001 (docs/33).
- **Open (provisioning, with owners):** FA-OPEN-009 frontier-LLM API credential(s) and initial routing configuration (Salim; needed before Week-2 LLM extractor tasks — dispatch of those tasks without credentials becomes BLOCKED_FOR_SALIM); FA-OPEN-010 RTX 5090 workstation connection + sizing re-derivation at owning tasks (Salim confirms availability; Week-2 stubs keep work unblocked); FA-OPEN-011 production auth provider (flagged OPEN by AMENDMENT-001; Salim decides at production phase; dev token path unblocked); FA-OPEN-012 Comtrade key decision (at Tier-1 activation).
- **Open (reserved to Salim by AMENDMENT-001):** FA-OPEN-018 any single mandatory frontier provider/model designation (interim: configuration-level routing, no hard-coded sole provider); FA-OPEN-019 production secrets/object-store hosting (interim: MinIO + WAL archiving + .env local dev per doc-28 self-hosted paths). Neither blocks Week-1.
- **Open (authority gap — MATERIAL for Week-1 activation tasks):** FA-OPEN-020 seed record values + Tier-0 onboarding checklists (docs 03/29/30 do not establish base URLs, reliability tiers, rate limits, collection modes; doc 29 requires human-approved checklists before `active`). AMENDMENT-002 does NOT supply these values. Minimal Salim decision package: approve a 16-row seed value table + 3 Tier-0 onboarding checklists. TASK-006 dispatch without it = BLOCKED_FOR_SALIM. TASK-001 is unaffected (schema only).
- **Open (documentation deltas):** FA-OPEN-001/002/003/004 resolved by human-approved ADR (doc-23 anti-drift rule) at the week that makes them material; FA-OPEN-005/006/007/008/013/014 carry DERIVED resolutions stated in §4.3/§7 for reviewer confirmation.
- **Open (source-identity semantics recorded by the §12 propagation sweep — FATH-V4-007):** **FA-OPEN-022** graph `source_refs` structural definition — docs 27/31/32 require every graph node/edge to carry non-empty `source_refs`, but the canonical doc-22 §3 DDL defines `provenance_fact_ids UUID[]` and no `source_refs` element; the referent (fact-level provenance chain vs direct source references) is not established by authority. Owned by the Week-2 Knowledge-Graph-Builder task plan; if resolved as direct persisted source references they MUST be UUIDs → `source_registry(source_id)` (docs/34 §6), and any new column beyond the doc-22 DDL requires a human-approved ADR (doc-23 anti-drift). **FA-OPEN-023** doc-15 UI-card provenance "source object IDs" — the referent object set is not defined by authority (registry sources vs the underlying evidence objects the card renders); every candidate referent is UUID-keyed under docs/34/03/04, so the identity FORM is settled (UUIDs, serialized per §9), but the referent SET is owned by the Canvas provenance task (Week 3) plan. Neither item blocks Week-1 tasks; both are recorded in PROPAGATION_MAP PM-J6/PM-J7 and REQUIREMENTS_TRACEABILITY.
- **GATE-SETUP (owned by Salim; REQUIRED BEFORE FIRST MERGE — explicit roadmap item):** branch protection on `main` + trusted exact-identity CI verification + receipts, each mechanically verified per §9. Until verified: trusted gates NOT_CONFIGURED / protection NOT_VERIFIED, all CI results are SHA-bound evidence only, and every candidate halts at REVIEW_APPROVED (not merge-eligible). Implementation and independent review of TASK-001 may proceed in parallel with GATE-SETUP; merging may not.

## 13. Explicitly out of scope for this bootstrap plan

- Any production application code (planner role boundary).
- Resolution of Week-2+ doc deltas beyond classification (owned by future task planning + ADRs).
- Governance changes, reviewer-independence changes, merge/release execution.
- Activation of any source beyond the doc-24 Week-1 set.

## 14. Plan identity and review

- Plan file: `.delivery/plans/FATH-BOOTSTRAP/BOOTSTRAP_PLAN.md`; SHA-256 recorded in the commit/handoff (computed over this exact file content).
- Companion artifacts: AUTHORITY_MANIFEST.json, DOCUMENT_READ_ORDER.md, REQUIREMENTS_TRACEABILITY.json, PROJECT_MAP.md, ROADMAP.md, TASK-001_PLAN.md, PROPAGATION_MAP.md, REMEDIATION-1_ADJUDICATION.md, REMEDIATION-2_ADJUDICATION.md, V4_ADJUDICATION.md.
- Independent reviewer: `plan-reviewer` (GPT-5.6 Sol, 1M, Max reasoning, fresh read-only context). Outcomes APPROVE / REJECT / BLOCKED; max 3 attempts per Escalation Policy §8; **this is review sequence 2, attempt 2 of 3** (sequence authorized by Escalation Policy §6 after the human-approved AMENDMENT-002; seq2 attempt-1 REJECT findings FATH-V4-001..009 adjudicated and corrected in `REMEDIATION-3_ADJUDICATION.md`; the prior V1–V3 sequence remains preserved unchanged in `.delivery/reviews/` and BUILD_STATE history).
