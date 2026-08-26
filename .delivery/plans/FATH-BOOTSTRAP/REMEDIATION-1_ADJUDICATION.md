# FATH-BOOTSTRAP — Remediation 1: Adjudication of Plan-Review Attempt-1 Findings

**Project:** FATH_AUTOPILOT · **Scope:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT / TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max)
**Findings record adjudicated:** `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-1.md` (commit `697adb4`, REJECT, 7 findings) against plan commit `3735813b4c7cddd41ac9251623fabbe505f3d298`.
**Outcome:** all seven findings adjudicated **VALID** after independent re-reading of the cited canonical sources; no finding challenged. Corrections produce plan v2 (review attempt 2 of 3).

Each adjudication below cites the authority re-read during this remediation, not the reviewer's text.

---

## FATH-PR-001 (BLOCKER) — seed authority gaps — **VALID**

**Re-verified:** doc 03 "Initial registry seeds" lists 16 seeds with only name, source class, and access preference; `SourceRegistryRecord` requires `base_url: AnyUrl` and `reliability_tier` with NO defaults; doc 03 `source_id: UUID` vs doc 29 DDL `source_onboarding_checklists.source_id TEXT PRIMARY KEY REFERENCES sources(id)` and doc 24 §1 / doc 30 textual ids; doc 29 "Every source must have a completed checklist before `active` status" + verifier item 8 (audited human approval); doc 30 verifier (YAML + checklist + rate limits per candidate). The reviewer is correct on every point: base URLs, tiers, rate limits, and collection modes are not established by authority; the identifier model is contradictory; activation without onboarding evidence would violate doc 29; and the prior A5/A6 could indeed have passed with invented records.

**Corrections:**
- TASK-001 **descoped to schema-only** (no seed rows, no `sources_seed.yaml` content, no loader); its fixtures are explicitly synthetic and labeled.
- Seed data, `config/sources_seed.yaml`, doc-29 `source_onboarding_checklists`, and Tier-0 activation evidence moved to **TASK-006**, gated on **FA-OPEN-020**: a Salim-approved seed value table (16 rows) + onboarding checklists for the three Tier-0 sources. TASK-006 dispatch without that approval = `BLOCKED_FOR_SALIM`. No values invented.
- Identifier model reconciled explicitly as **DERIVED (FA-OPEN-021,** reviewer confirms**)**: `source_registry.id TEXT PRIMARY KEY` — doc-29's TEXT FK is only satisfiable with a TEXT key; doc 24 §1 (which outranks doc 03) and doc 30 use textual ids; doc-03's UUID default superseded on this one field only.
- Artifacts changed: TASK-001_PLAN §§1–10; BOOTSTRAP_PLAN §§2, 3, 4.3, 7.4, 12; ROADMAP Week-1 table + open items; traceability FA-REQ-W1-001/003 + new FA-OPEN-020/021; manifest FA-DOC-03 relationships.

## FATH-PR-002 (HIGH) — layout deviation without ADR — **VALID**

**Re-verified:** doc 16 canonical layout has `safety/` (owning Access Guard + Trust Boundary), `budgets/` (plural), `db/connection.py`, `db/migrations/`, tests under `src/fath/tests/{fixtures,unit,integration}`; no `sources/`, `trust/`, `budget/`, or `audit/` modules. Doc 23 anti-drift: new module paths need an ADR-style note **with human approval**. The prior TASK-001 §4.1 listed non-canonical modules and top-level `migrations/`/`tests/` while claiming doc-16 conformance.

**Corrections:** TASK-001 §4.1 now scaffolds exactly the doc-16 module set; migrations under `src/fath/db/migrations/`; tests under `src/fath/tests/`; non-doc-16 root additions explicitly enumerated and justified (`.gitignore`, `.env.example`, `alembic.ini`, `Makefile`, `docker/postgres/`, `.github/workflows/` — none are module paths). New acceptance criterion **A5 (layout conformance)** with a SPECIFIED doc-16 oracle (scripted tree comparison in CI). New stop condition: any needed non-doc-16 module path → STOP for human-approved ADR.

## FATH-PR-003 (HIGH) — impossible A8, oracle-less A9 — **VALID**

**Re-verified:** docs/33 verifier item 1 scopes the A100 prohibition to "implementation, configuration, or sizing"; the canonical docs necessarily contain the amended terms; my prior A8 said "repo-wide". A9 had no scanning oracle (oracle policy requires defined comparison methods).

**Corrections:** A8 rescoped to an explicit implementation/configuration scan set (`src/`, `docker/`, `.github/`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `Makefile`, `alembic.ini`, `.env.example`) with explicit exclusions (`docs/`, `.delivery/`, README doc citations). A9 now specifies pinned-version **gitleaks** (PROPOSED tool, recorded in BOOTSTRAP_PLAN §4.4) over the candidate tree + gitignore test. Both run in CI.

## FATH-PR-004 (HIGH) — "zero-LLM Week 1" misclassified as necessary — **VALID**

**Re-verified:** doc 14 "Initial budget defaults" permits `daily_ingestion: max_llm_calls: 200` (only the hourly source check is 0); doc 18 states "The model may output JSON UI specs"; doc 07 defines validate → reject → retry-once → fallback orchestrator semantics. My DERIVED claim generalized the hourly-heartbeat zero to the whole week; that was an overreach.

**Corrections:** reclassified as **PROPOSED** (BOOTSTRAP_PLAN §4.4) with defined behavior: Week-1 Canvas v0 uses a deterministic event→component spec producer behind a producer interface; the full doc-07 validation/retry/fallback pipeline is implemented and fixture-tested in Week 1; the model producer plugs into the same interface in Week 2 behind the provider-agnostic LLM client (which precedes ALL model-driven consumers — DERIVED row updated). Rationale: FA-OPEN-009 credentials unprovisioned + AMENDMENT-001 requires the client abstraction first. The stated alternative if the proposal is rejected: schedule the LLM-client task inside Week 1, placing Week 1 behind FA-OPEN-009. ROADMAP Week-1 header and traceability updated consistently.

## FATH-PR-005 (MEDIUM) — image strategy misclassified; versions unpinned — **VALID**

**Re-verified:** docs 02/22/28 require one PG16 instance with the extensions; they do not mandate a custom-image packaging method; alternatives exist. "Logically necessary" was wrong.

**Corrections:** reclassified as **PROPOSED** (BOOTSTRAP_PLAN §4.4; TASK-001 §4.4): base image pinned by digest, AGE + pgvector pinned to exact release tags recorded in the Dockerfile; changing a pin is a reviewed change. New acceptance criterion **A11**: functional extension checks (vector(1024) column + HNSW index creation; AGE graph creation + cypher query).

## FATH-PR-006 (HIGH) — candidate-controlled CI mislabeled trusted — **VALID**

**Re-verified:** review policy §§36–39 (trusted mechanisms must be outside candidate control); BUILD_STATE shows no protected CI/branch protection/receipts. My §4.2 called CI "trusted verification" while §9 admitted no trusted-receipt claim — an internal contradiction.

**Corrections:** every occurrence relabeled: TASK-001 CI is **SHA-bound test evidence**; trusted-gate status **NOT_CONFIGURED** stated in BOOTSTRAP_PLAN §§4.2/9, TASK-001 §§4.8/6(A10)/11, traceability FA-REQ-CP-001, and ROADMAP governance; trusted-mechanism setup (protected CI + branch protection + receipts, owner Salim) is an explicit roadmap item.

## FATH-PR-007 (MEDIUM) — Entra presented as specified; ADR path omits human approval — **VALID**

**Re-verified:** docs/33 flags the production auth provider OPEN (my FA-OPEN-011 was corrected earlier, but FA-REQ-W5-001 still read "Entra OIDC in production"); doc 23 anti-drift requires "an ADR-style note and receive human approval".

**Corrections:** FA-REQ-W5-001 now states the production provider is OPEN per docs/33 (dev token per doc 25); FA-OPEN-004's resolution path (and every ADR mention in the corrected artifacts) now requires explicit human (Salim) approval per doc 23.

---

## Artifacts changed in this remediation

| Artifact | Change |
|---|---|
| TASK-001_PLAN.md | Rewritten (v2): schema-only scope, doc-16-exact layout, A5 layout oracle, A8/A9 rescoped oracles, A11 functional checks, PROPOSED image pins, CI relabeled, new stop conditions |
| BOOTSTRAP_PLAN.md | v2: readiness §2 (FA-OPEN-020 materiality), §3 rows, §4.2 CI relabel, §4.3/§4.4 reclassifications (image, Week-1 posture), §7.4 identifier resolution, §9 rewritten, §12 open items, §14 attempt 2 |
| ROADMAP.md | Week-1 LLM posture PROPOSED note; TASK-001/TASK-006 rescoped (FA-OPEN-020 gate); CI/trusted-mechanism governance item; open-items list |
| REQUIREMENTS_TRACEABILITY.json | FA-REQ-W1-001/003 split + gates; FA-REQ-CP-001 relabel; FA-REQ-W5-001 auth fix; FA-OPEN-004 human approval; new FA-OPEN-020/021 |
| AUTHORITY_MANIFEST.json | FA-DOC-03 relationships note (identifier/seed deltas) |
| DOCUMENT_READ_ORDER.md, PROJECT_MAP.md | Unchanged (project map §2 was already doc-16 conformant; verified) |

## New open items

- **FA-OPEN-020** (MATERIAL, gates TASK-006 → TASK-007/008/014): Salim-approved seed value table + Tier-0 onboarding checklists.
- **FA-OPEN-021** (DERIVED resolution for reviewer confirmation): TEXT slug identifier model.

No new blockers for bootstrap or TASK-001. This record is planning material, not project authority; it approves nothing.
