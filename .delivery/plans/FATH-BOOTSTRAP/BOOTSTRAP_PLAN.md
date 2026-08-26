# FATH_AUTOPILOT — Project Bootstrap and Architecture Plan

**Plan ID:** FATH-BOOTSTRAP-PLAN v1
**Project:** FATH_AUTOPILOT · **Repo:** baramiSG/Fath_Autopilot · **Baseline:** `ae5a4ea7db30d9ba243e29c98424702f5e0fb7a1`
**Author role:** CHIEF_ARCHITECT · **Model:** Claude Fable 5 (1M, Thinking ON, Max)
**Status:** PLAN_READY_FOR_INDEPENDENT_REVIEW (plan_review_attempt 1) — this plan is NOT self-approved and authorizes no implementation until independent Sol review returns APPROVE.

This plan is operational planning material, not new project authority. Canonical authority remains `docs/` — with `docs/33_AMENDMENT_001_COMPUTE_AND_LLM_PROVIDER.md` (AMENDMENT-001, HUMAN_APPROVED_AMENDMENT) at the **top of project-document precedence**, then doc 24 overriding docs 00–23 where they conflict for everything the amendment does not address. Classifications used: **SPECIFIED / DERIVED / PROPOSED / OPEN / BLOCKED** per control-plane constitution §6.

**AMENDMENT-001 (material authority change, incorporated throughout this plan):** no A100 GPUs (the "8×A100 VM" is void); local GPU compute target is a **single NVIDIA RTX 5090 workstation**; **no Azure OpenAI** anywhere (no SDK, endpoint, deployment name, or environment variable); agent reasoning uses **frontier LLM APIs via a provider-agnostic client with configurable model routing** (doc-02's "no extra frontier LLMs" clause reversed); every earlier "GPT-5.4" mention reads as "the configured frontier reasoning model, accessed via API" with vision fallback staying fallback-only; security invariants (crawler never calls the reasoning model, trust boundary, budget/rate/breaker governance) unchanged. Amendment file sha256 `3ea00519a4e7b79adb2e1f60afcfd4c393906033c148fd254fb1d71e15c61589`, verified and committed alone as `234a24d9e012710352d35aa5b1314a6395614945` before any plan artifact.

---

## 1. Authority basis

Read in full at baseline commit: docs 00–32, docs/README.md (all 34 canonical files; hashes recorded in `AUTHORITY_MANIFEST.json`), plus a sample of the combined file confirming it is a concatenation (REFERENCE_ONLY). Read in full after controller interrupt: docs/33 AMENDMENT-001 (hash verified against the controller-supplied expected value before commit; committed at `234a24d9e012710352d35aa5b1314a6395614945`). Control-plane governance read in full: constitution, role/model policy, oracle policy, review/acceptance policy, escalation policy, governance baseline, BUILD_STATE.yaml.

## 2. Build-readiness assessment

**Classification: `READY_WITH_NON_MATERIAL_OPEN_ITEMS`**

| Readiness input | Status | Evidence |
|---|---|---|
| Canonical authority documents | Present | 34 canonical files + AMENDMENT-001 (docs/33), all hashed in manifest |
| Intended outcomes | Present | docs/00, 01 (incl. 10 six-week success criteria) |
| Requirements | Present | docs 03–16, 21–22, 25–30 (contract-level Pydantic/SQL/algorithms) |
| Acceptance criteria | Present | docs/23 Week-1 done criteria; docs/17 per-week verification; docs/27 quality gates; docs/32 readiness checklist |
| Business/domain rules | Present | docs/01, 03, 11, 12, 29, 30 |
| Architecture | Present and locked | docs/00, 02 (+ 16 layout, 22 DB detail) |
| Data assumptions | Present | docs/03, 04, 29, 30 (public data only; five stores; provenance mandatory) |
| Integration assumptions | Present | docs/03, 09, 30 (source classes, access modes) |
| Security constraints | Present | docs/00, 05, 12, 19, 25, 26 (+ 24 corrections) |
| Environment constraints | Present | docs/33 AMENDMENT-001 (RTX 5090 workstation; frontier LLM APIs), 28 (services, secrets; Azure hosting options OPEN per 33) |
| Verification expectations | Present | docs/17, 23, 27, 31, 32 |
| Material unresolved decisions | None blocking Week-1 | Open items FA-OPEN-001..014, 018, 019 are non-material now or have specified fallbacks (see §12) |

Material missing authority for the Week-1 scope: **none found**. All open items either (a) have doc-24 resolutions, (b) are future-week provisioning (credentials/GPU/OIDC) with specified interim paths (deterministic Week-1 pipeline, stubbed embeddings, dev auth), or (c) are minor documentation inconsistencies with documented resolution paths that do not affect the foundation slice.

## 3. Material contradictions found and their classification

Full register: `REQUIREMENTS_TRACEABILITY.json → open_items`. Summary:

| Item | Conflict | Classification |
|---|---|---|
| A100 / Azure OpenAI (former locked stack) | docs 00/02/18/21/README "Azure OpenAI GPT-5.4 only", "8×A100 VM", "no extra frontier LLMs" vs owner instruction | **RESOLVED_BY_AMENDMENT_001 (SPECIFIED)** — RTX 5090 workstation; provider-agnostic frontier-LLM API client; interpretation rules for all GPT-5.4 mentions |
| FA-OPEN-016 | doc 04 global `UNIQUE(content_hash_sha256)` vs doc 24 §2 provenance-preserving inserts | **RESOLVED_BY_24** — no global hash uniqueness; session duplicate guard index instead |
| FA-OPEN-017 | doc 04 FactLifecycle vs doc 24 §3 FactStatus | **RESOLVED_BY_24** — FactStatus + transition map govern |
| FA-OPEN-015 | doc 23 Week-1 Al Meezan collector criterion vs doc 24 §1 / doc 18 | **RESOLVED_BY_24** — registry definition only; no Week-1 collection |
| FA-OPEN-001 | Canvas registry delta (24 §4 vs 07) | **OPEN** (non-material until Week 3/6; ADR then) |
| FA-OPEN-002 | grounding similarity 0.72 (10, 11) vs 0.68 (21) | **OPEN** (material Week 5; ADR then) |
| FA-OPEN-003 | embedding namespace lists (10 vs 21) | **OPEN** (material Week 2; ADR then) |
| FA-OPEN-004 | module paths (31 vs 16) | **OPEN** (material Week 2; ADR then per doc-23 anti-drift rule) |
| FA-OPEN-005/013 | migration numbering; Week-1 minimal facts vs Week-2 full store | **OPEN→DERIVED** sequencing (illustrative numbering; minimal-then-full) |
| FA-OPEN-006/007/008 | table naming, event casing, blob field naming | **OPEN→DERIVED** naming resolutions (§7) |
| FA-OPEN-009..012 | frontier-LLM API keys, RTX 5090 workstation connection + sizing re-derivation, production auth provider (flagged OPEN by 33), Comtrade key | **OPEN** provisioning (future weeks; interim paths specified) |
| FA-OPEN-018/019 | mandatory frontier provider designation; production secrets/object-store hosting | **OPEN** per AMENDMENT-001 (reserved to Salim; config-level routing and self-hosted interim paths keep all weeks unblocked) |

No `BLOCKED` and no `BLOCKED_FOR_SALIM` items exist for the bootstrap or TASK-001 scope.

## 4. Architecture decisions by classification

### 4.1 SPECIFIED (locked by docs/00 §Locked technology decisions and docs/02, as amended by AMENDMENT-001; not renegotiable without ADR, and never against AMENDMENT-001)

| Decision | Source |
|---|---|
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
| Secrets: .env local only; never in logs/audit/events; production secrets hosting OPEN per AMENDMENT-001 (doc-28 Key Vault option not voided, not confirmed) | 28; 33 (Flagged OPEN) |
| Week-1 active sources exactly Qatar Open Data, World Bank, GDELT | 24 §1, 23, 30 |

### 4.2 SPECIFIED by control-plane governance (not by project docs)

| Decision | Source |
|---|---|
| uv for Python dependency/environment management; type hints on public functions; no bare except | SG-TR-007 (control plane). Project docs specify pyproject.toml (16) and name no package manager — no conflict. |
| Independent review binds to exact candidate SHA; task branches + PRs to main; no self-approval | Control-plane constitution §8, review policy §16–21 |
| Deterministic CI as trusted verification for the target repo | Constitution §9/§19 (repo currently has NO CI — see §9) |

### 4.3 DERIVED (logically necessary; derivation stated)

| Decision | Derivation |
|---|---|
| Custom Postgres image bundling PG16 + AGE + pgvector for docker-compose and CI | Docs 02/22/28 require all three in ONE instance; no single official image ships both extensions; a pinned Dockerfile is the minimal way to satisfy the specified stack. Implementer chooses the base (e.g. build AGE + pgvector into postgres:16) provided versions are pinned and extensions verifiably load. |
| Postgres event outbox table + Redis Streams transport coexist | Doc 06 rejects a Postgres event BUS; docs 22/23 require durable event_outbox storage; reconciled as transport vs durable record (FA-REQ-W1-009). |
| Week-1 pipeline is fully deterministic (zero reasoning-model calls) | Doc 14 hourly budget `max_llm_calls: 0`; Week-1 fact criterion satisfiable via `deterministic_api` extraction (doc 04 enum); doc 06/24 event→component mapping is deterministic; therefore no frontier-LLM API credential is a Week-1 dependency (and per AMENDMENT-001 no Azure OpenAI artifact may exist at any point). |
| The provider-agnostic LLM client is a Week-2 prerequisite task, built before any extractor task | AMENDMENT-001 mandates the abstraction for all agent reasoning; doc-31 extractors are its first consumers; sequencing it first avoids per-extractor provider coupling. Its module path is not in the doc-16 layout — Week-2 planning resolves placement by ADR (doc-23 anti-drift rule, folded into FA-OPEN-004). |
| Migration sequencing: numbering assigned in creation order; first facts-creating migration carries full FactStatus | Doc 24 §3 + doc 23 (“first fact migration”); doc-31 filenames treated as illustrative (FA-OPEN-005). |
| Week 1 minimal Fact Store slice; Week 2 full store | Doc 23 done criteria vs doc 17 Week-2 “full implementation” (FA-OPEN-013). |
| Frontend scaffolding deferred to the Canvas frontend task (not TASK-001) | Doc-16 layout includes frontend/, but no Week-1 criterion tests frontend existence before Canvas v0; deferring keeps candidates bounded and reviewable (constitution §7). |

### 4.4 PROPOSED (reversible engineering choices — reviewer may reject without touching authority)

| Proposal | Rationale |
|---|---|
| Python 3.11 as interpreter baseline | Not specified anywhere in docs. 3.11 chosen for widest wheel compatibility with the locked ML tooling arriving in Weeks 2–4 (unstructured.io, PaddleOCR, Nougat, vLLM ecosystems historically lag newest CPython). Reversible via pyproject change + ADR note. |
| GitHub Actions as the CI platform | Repo is GitHub-hosted; Actions gives SHA-bound required checks usable for branch protection and future trusted receipts. Reversible. |
| Dev tooling: ruff (lint+format) + mypy (strict on src/) + pytest | Enforces SG-TR-007 mechanically; doc 16 requires typed functions. Reversible. |
| SQLAlchemy 2.x + asyncpg as DB access layer under the memory services | Doc 24 §8 shows SQLAlchemy session patterns (evidence the corpus assumes SQLAlchemy); async matches FastAPI. Reversible. |
| Canonical physical table names per §7 | See §7; reviewer confirms. |

## 5. Repository scaffolding plan (what the foundation must create)

Target-state tree: `PROJECT_MAP.md §2` (doc 16 + control-plane additions `.delivery/`, `.github/workflows/`, plus `golden/`, `scripts/`, `Makefile` required by docs 27/28/31). Scaffolding is delivered incrementally by bounded tasks (ROADMAP.md); TASK-001 creates the package skeleton, config, DB foundation, and CI (TASK-001_PLAN.md).

## 6. Environment and dependency baseline

- **Runtime services (local/dev):** docker-compose with `postgres` (custom PG16+AGE+pgvector image, pinned), `redis:7` (pinned). MinIO added by the Raw-Archive task; Prefect/vLLM/sandbox services added when their tasks arrive. (SPECIFIED set; incremental introduction is DERIVED from bounded-task discipline.)
- **Python:** uv-managed `pyproject.toml` + committed `uv.lock`. TASK-001 dependency baseline is minimal (pydantic v2, pydantic-settings, SQLAlchemy 2, alembic, asyncpg, psycopg[binary] for migrations if needed, redis-py, PyYAML; dev: pytest, ruff, mypy, testcontainers or compose-driven test harness). Each later dependency (fastapi, langgraph, prefect, unstructured, …) enters ONLY with the task that uses it, with the doc that specifies it cited in that task's plan (dependency discipline).
- **Secrets:** `.env.example` with placeholder keys named per doc 28 **excluding every Azure OpenAI variable** (AMENDMENT-001 verifier item 2: no Azure OpenAI environment variable may exist); frontier-LLM API key names enter with the Week-2 LLM-client task as configuration; real `.env` git-ignored; no secret in any artifact.

## 7. Naming resolutions (DERIVED; reviewer to confirm — FA-OPEN-006/007/008)

1. **Physical table names:** `source_registry`, `access_decisions`, `raw_archive` (+ doc-22 names for tables only doc 22 defines). Basis: docs 03/04 define these names including FK references (`raw_archive.access_decision_id → access_decisions.decision_id`); doc 24's `sources`/`raw_archive_records` snippets state semantic corrections (status column, duplicate guard), each section's stated purpose being behavior, not renaming. Doc-24 semantics are applied verbatim to the canonical names.
2. **Event types:** doc-06 catalog CamelCase names are canonical; snake_case mentions in docs 05/09/12 map to their catalog equivalents.
3. **UntrustedBlob fields:** doc-05 field contract governs; doc-24 §7 immutability (`model_copy`), delimiter escaping, and a truncation flag are binding additions.

If the plan reviewer rejects any of these readings, the correction is a plan remediation, not an implementation-time improvisation.

## 8. Security and data boundaries (plan-level)

- **Trust boundary:** all external content wrapped as UntrustedBlob with sanitization, injection scoring, quarantine ≥ 0.85, delimiter escaping; no raw web text as instructions (docs 05, 24 §7; verified by fixture tests before any continuous crawling — doc 27 security gates).
- **Module boundaries as security controls:** crawlers cannot import the LLM router; extractors cannot write hypotheses; UI cannot modify analysis records (docs 08, 16 — enforced by architecture tests).
- **Action restriction:** no external-action code paths; approvals RBAC-enforced in backend when introduced (docs 00, 25, 24 §12); RBAC required before Week-5 publication/quarantine flows (doc 25 build order).
- **Data:** public sources only; PII rules per doc 29; no LMIS/QNWIS/ministry-private data anywhere.
- **Secrets:** never committed, never logged, never in prompts or artifacts (doc 28 + control-plane §17). The spec corpus itself is Salim-authored, non-client material — permitted in this seat.
- **Sandbox (Week 4):** no-network container, blocked imports, resource caps (doc 26).

## 9. CI plan (deterministic CI is currently NOT configured — this plan establishes it)

**Platform (PROPOSED):** GitHub Actions in `.github/workflows/ci.yml`, created by TASK-001.

**Pipeline (every push/PR, bound to exact SHA):**
1. `uv sync --frozen` (lockfile integrity).
2. `ruff check` + `ruff format --check`.
3. `mypy src/` (strict; SG-TR-007 hint enforcement).
4. Build the pinned PG16+AGE+pgvector image; start it + Redis 7 as services.
5. `alembic upgrade head` → `pytest` (unit + integration) → `alembic downgrade base` → `alembic upgrade head` (doc-28 migration cycle).
6. Fail on any warning-level lint error, type error, test failure, or migration asymmetry.

**Determinism rules:** pinned image digests/versions, `uv.lock` frozen, no network calls in tests (connectors tested against recorded/golden fixtures — doc 27 pattern), fixed random seeds where randomness exists (oracle policy §27).

**Trusted-gate trajectory:** CI green on candidate SHA becomes a required input to merge eligibility. Branch protection on `main` (require CI + reviewed SHA match) needs repo-admin action by **Salim** — recorded as recommendation, not assumed done (fail-closed: until protection exists, merge eligibility is asserted by controller process, and no trusted-receipt claim is made — constitution §9).

## 10. Test strategy (evidentiary, per oracle policy)

- **Layer 1 — contract tests (SPECIFIED oracles):** every Pydantic model validated with golden-positive and golden-negative fixtures derived from doc contracts (invalid enum, out-of-range confloat, missing provenance, unknown fields where forbidden).
- **Layer 2 — behavior tests (SPECIFIED oracles):** the doc-listed minimum tests are mandatory floors: doc 05 (6 trust-boundary tests + spoofing test from 24 §7), doc 06 (7 event-bus tests), doc 09 (6 crawler tests), doc 24 verifier checklist items, doc 23 done criteria.
- **Layer 3 — integration (SPECIFIED):** migration cycles, extension presence, end-to-end Week-1 heartbeat smoke (TASK-014) with recorded evidence.
- **Layer 4 — golden evaluation (REFERENCE oracles, Week 2+):** `golden/` datasets with provenance per doc 27; `make eval` producing EvalReport bound to git commit; thresholds per doc 27 tables. Golden files change only via oracle-change review (oracle policy §13).
- **Layer 5 — security regression (SPECIFIED):** injection fixtures, delimiter spoofing, boundary-import tests, RBAC fixtures (Week 5), sandbox no-network tests (Week 4) — the doc-27 security gates run before any continuous autonomous operation.
- **Negative evidence:** for consequential logic, tests must fail when a sign/threshold/field is wrong (oracle policy §11) — e.g. audit chain tamper detection, wrong-hash rejection, budget breach continuing would fail.
- Tests never weaken oracles to pass; conflicts stop work and surface (oracle policy §38).

## 11. Governed Git workflow for this project

- `main`: protected target branch; only PR merges after gates.
- `plan/*`: planning artifacts (this branch: `plan/bootstrap-and-task-001`).
- `task/TASK-XXX-<slug>`: one branch per bounded task, cut from current `main` (TASK-001 branches from the merged plan baseline once this plan is approved; the controller manages merge of the plan branch).
- Implementer produces an immutable candidate commit; review binds to that exact SHA; any change → new candidate → fresh review (review policy §16–21, escalation ladder per escalation policy).
- Commits: imperative, task-scoped messages referencing the task ID; no history rewrites on shared branches; merge only when merge-eligibility inputs recorded in BUILD_STATE are satisfied.
- `.delivery/` in this repo holds plan/evidence artifacts; durable workflow state lives in the control-plane BUILD_STATE.yaml (single source of truth for counters/states).

## 12. Open items and blockers

- **Blockers:** none for bootstrap or TASK-001.
- **Open (provisioning, with owners):** FA-OPEN-009 frontier-LLM API credential(s) and initial routing configuration (Salim; needed before Week-2 LLM extractor tasks — dispatch of those tasks without credentials becomes BLOCKED_FOR_SALIM); FA-OPEN-010 RTX 5090 workstation connection + sizing re-derivation at owning tasks (Salim confirms availability; Week-2 stubs keep work unblocked); FA-OPEN-011 production auth provider (flagged OPEN by AMENDMENT-001; Salim decides at production phase; dev token path unblocked); FA-OPEN-012 Comtrade key decision (at Tier-1 activation).
- **Open (reserved to Salim by AMENDMENT-001):** FA-OPEN-018 any single mandatory frontier provider/model designation (interim: configuration-level routing, no hard-coded sole provider); FA-OPEN-019 production secrets/object-store hosting (interim: MinIO + WAL archiving + .env local dev per doc-28 self-hosted paths). Neither blocks Week-1.
- **Open (documentation deltas):** FA-OPEN-001/002/003/004 resolved by ADR at the week that makes them material; FA-OPEN-005/006/007/008/013/014 carry DERIVED resolutions stated in §4.3/§7 for reviewer confirmation.
- **Recommendation to Salim (non-blocking):** enable GitHub branch protection on `main` once TASK-001's CI lands (§9).

## 13. Explicitly out of scope for this bootstrap plan

- Any production application code (planner role boundary).
- Resolution of Week-2+ doc deltas beyond classification (owned by future task planning + ADRs).
- Governance changes, reviewer-independence changes, merge/release execution.
- Activation of any source beyond the doc-24 Week-1 set.

## 14. Plan identity and review

- Plan file: `.delivery/plans/FATH-BOOTSTRAP/BOOTSTRAP_PLAN.md`; SHA-256 recorded in the commit/handoff (computed over this exact file content).
- Companion artifacts: AUTHORITY_MANIFEST.json, DOCUMENT_READ_ORDER.md, REQUIREMENTS_TRACEABILITY.json, PROJECT_MAP.md, ROADMAP.md, TASK-001_PLAN.md.
- Independent reviewer: `plan-reviewer` (GPT-5.6 Sol, 1M, Max reasoning, fresh read-only context). Outcomes APPROVE / REJECT / BLOCKED; max 3 attempts; this is attempt 1.
