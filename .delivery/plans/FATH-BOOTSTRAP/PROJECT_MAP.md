# Fath Autopilot — Project Map

**Artifact type:** Navigation aid (NOT project authority; NOT architecture authority)
**Project:** FATH_AUTOPILOT · **Task:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT
**Baseline commit:** `ae5a4ea7db30d9ba243e29c98424702f5e0fb7a1`

> **WARNING.** This map assists future agents. It does not become architecture authority merely because it is convenient. The canonical documents under `docs/` (with `docs/34` AMENDMENT-002 and `docs/33` AMENDMENT-001 at the top of precedence — 34 wins over everything earlier where conflicting — then `docs/24` overriding 00–23 where they conflict) remain authoritative. At the plan-V5 state, the repository contains **only `docs/` and `.delivery/`** — everything under "Intended repository structure" is the doc-16 target state, not existing code.

## 1. Current repository state (verified at baseline)

```text
Fath_Autopilot/
  docs/          36 canonical documents — 00–34 + README (see AUTHORITY_MANIFEST.json); the combined file is REFERENCE_ONLY and not counted
  .delivery/     delivery-governance artifacts (this planning package)
```

No source code, no CI, no dependency manifest exists yet. Git remote: `origin = https://github.com/baramiSG/Fath_Autopilot.git`; branches: `main`, `plan/bootstrap-and-task-001`.

## 2. Intended repository structure (authority: docs/16, root files per docs/16 + control-plane additions)

```text
fath-autopilot/  (this repo root)
  docs/                        canonical authority corpus (do not edit as implementation side effect)
  docs/adr/                    ADRs superseding locked decisions (doc 02 supersession rule; none yet)
  src/fath/
    config/                    settings.py, sources_seed.yaml, execution_rules.yaml
    db/                        connection.py, migrations/ (Alembic), models/ (one file per store/table group)
    memory/                    write services for the five stores (agents never write SQL directly)
    safety/                    trust_boundary.py, injection_patterns.yaml, access_guard.py, source_poisoning.py
    crawlers/                  base.py + api/legal/report/news_event/benchmark crawlers (NO LLM imports)
    parsers/                   html/pdf/table/ocr/nougat parsers
    extractors/                base + economic_indicator/legal_constraint/trade_flow/company_disclosure/policy_claim
    graph/                     age_client.py, entity_resolver.py, graph_builder.py, graph_queries.py
    embeddings/                chunker.py, embedder.py, vector_store.py, retrieval.py
    agents/                    source_scout, change_detector, anomaly_miner, connection_agent,
                               coverage_auditor, hypothesis_generator, policy_genome_generator,
                               causal_skeptic, briefing_composer
    validators/                sanad.py + five chain modules
    workflows/                 states.py, source_check.py, ingestion.py, graph_anomaly.py,
                               coverage_audit.py, policy_tournament.py, briefing.py
    events/                    schemas.py, event_log.py, consumers.py
    budgets/                   redis_budget.py, token_counter.py, circuit_breakers.py
    ui/                        schemas.py, orchestrator.py, run_replay.py, approval_marshal.py
    api/                       main.py, routes/{events,ui,sources,investigations,approvals}.py
    tests/                     fixtures/, unit/, integration/   (doc-16 places tests under src/fath/)
  frontend/                    Next.js + React + TypeScript
    app/                       app router
    components/                registry.tsx + the approved Canvas components (doc 07 / doc 24 §4)
    lib/                       types.ts, api.ts, sse.ts
  golden/                      golden datasets (doc 27 structure; Week 2+)
  scripts/                     operational scripts (verify_audit_chain.py etc., doc 28 runbooks)
  pyproject.toml               Python project (uv-managed per control-plane SG-TR-007)
  docker-compose.yml           local stack (doc 16 root)
  Makefile                     make test / make eval targets (docs 31, 27, 23)
  README.md                    repo readme (doc 16 root)
  .delivery/                   delivery-governance artifacts (control-plane addition, not in doc 16)
  .github/workflows/           deterministic CI (control-plane addition, not in doc 16 — see BOOTSTRAP_PLAN)
```

## 3. Major runtime services (authority: docs/02, 28)

| Service | Role | First needed |
|---|---|---|
| Postgres 16 + Apache AGE + pgvector | Single operational DB: relational stores, graph (relational canonical + AGE mirror), vectors, audit log, event outbox | TASK-001 |
| Redis 7 | Streams event bus transport, budget counters, locks, circuit breakers (never source of truth) | TASK-001 (infra), TASK-004/009 (use) |
| FastAPI backend | API + SSE streaming to Canvas | TASK-012 |
| Next.js frontend | Fath Canvas (controlled generative UI) | TASK-013 |
| Prefect 3 server/worker | Heartbeat scheduling | TASK-011 |
| MinIO (dev; prod hosting OPEN per AMENDMENT-001) | Raw artifact object storage | TASK-003 |
| Embedding/reranker serving, OCR workers | BGE-M3 embeddings, OCR, reranking — sized for the single RTX 5090 workstation (AMENDMENT-001; no A100s) | Week 2+ (stubbable) |
| Simulation sandbox worker | No-network template simulation container | Week 4 |
| Caddy reverse proxy | Production ingress | Production |

## 4. Datastores and key tables (authority: docs/04, 22, 15, 25, **34**; naming resolution in BOOTSTRAP_PLAN §7)

- **Source identity (docs/34 AMENDMENT-002 — governing):** `source_registry` is the single canonical source table (NO `sources` table); `source_id UUID PRIMARY KEY` immutable; `slug TEXT NOT NULL UNIQUE` readable/config identifier; every persisted source FK → `source_registry(source_id)`, never `slug` absent a human-approved ADR; transport `source_id` strings = serialized UUIDs; per-surface mapping in `PROPAGATION_MAP.md`.
- **Five memory stores:** raw_archive, fact_store/facts, hypothesis_store/hypotheses, insight_corpus/insights, belief_calibration.
- **Registry/control:** source_registry, access_decisions, source_onboarding_checklists (UUID FK per docs/34 §7), source_terms_snapshots (UUID FK per docs/34 §7).
- **Events/audit:** event_outbox, idempotency_keys, audit_log (hash-chained, append-only).
- **Graph:** graph_nodes, graph_edges (relational canonical) + AGE graph `fath_economic_graph` (mirror).
- **Vectors:** document_chunks, embeddings (pgvector HNSW).
- **Workflow/budget:** workflow_runs, budget_policies, budget_reservations, llm_usage.
- **Auth/approvals (Week 5+):** users, approval_requests, approval_decisions, approval_policies.
- **Quality/ops:** eval_reports, restore_reports, incident_reports, sanad_validations, source_poisoning_alerts, scenario_runs.

## 5. Interfaces

- **REST/SSE (FastAPI):** routes for events, ui, sources, investigations, approvals (doc 16); `/healthz`, `/readyz`, `/metrics` (doc 28); SSE stream with RBAC filtering (doc 25).
- **Event bus:** 14 Redis streams `events:*` (doc 06) with consumer groups and `<stream>:dlq`.
- **UI contract:** JSON ComponentSpec validated backend (Pydantic) and frontend (Zod); approved components only.

## 6. External integrations (Week-1 active set per doc 24 §1)

Active Week 1: Qatar Open Data, World Bank, GDELT (API/download).
Defined-inactive (candidate_manual_review): Al Meezan, QCB, QSE, Invest Qatar.
Backlog tiers and activation order: doc 30. Reasoning: frontier LLM APIs via a provider-agnostic client with configurable routing (AMENDMENT-001; Week 2+; zero reasoning-model calls in the Week-1 path). No Azure OpenAI anywhere.

## 7. Configuration and secrets

- `src/fath/config/settings.py` (pydantic-settings), `sources_seed.yaml`, `execution_rules.yaml`, `injection_patterns.yaml`.
- Local dev: `.env` (never committed; `.env.example` committed). Production secrets hosting: OPEN per AMENDMENT-001 (doc-28 Key Vault option not voided, not confirmed; self-hosted interim operative). No secret ever enters audit log, structured logs, event payloads, Canvas specs, or raw archive. No Azure OpenAI environment variables may exist (AMENDMENT-001 verifier item 2).

## 8. Tests and verification

- Per-module tests under `src/fath/tests/` (doc 16 convention: schema validation, idempotency, failure behavior, security boundary).
- Injection fixtures `tests/fixtures/injection/` (doc 05); golden datasets `golden/` (doc 27, Week 2+); `make eval` EvalReports; weekly regression workflow (doc 27).
- Deterministic CI on every candidate SHA (control-plane requirement; see BOOTSTRAP_PLAN §9).

## 9. Where authority lives (quick pointers)

| Question | Authority |
|---|---|
| What is locked technologically? | docs/00, 02 as amended by docs/33 and docs/34 (+ ADRs under docs/adr/ when created) |
| What overrides what? | docs/34 (AMENDMENT-002) over everything earlier incl. 33 and 24 where conflicting; docs/33 (AMENDMENT-001) over README + 00–32 incl. 24; then docs/24 over 00–23; see AUTHORITY_MANIFEST precedence_rules |
| Source identity (any `source_id`/`slug` question)? | docs/34 AMENDMENT-002 (UUID PK + unique slug on source_registry; FK/transport/YAML rules); per-surface map: `PROPAGATION_MAP.md` (aid) |
| Compute platform and reasoning provider? | docs/33 AMENDMENT-001 (RTX 5090 workstation; frontier LLM APIs, provider-agnostic client; no Azure OpenAI) |
| What must Week 1 deliver? | docs/17 (Week 1), 18, 23 done criteria — as corrected by 24 §1 |
| Schemas for stores/events/UI? | docs/04, 06, 07 (+ 24 corrections), 21, 22 |
| Security boundaries? | docs/05, 12, 19, 25, 26 (+ 24 §§7,9,10,12) |
| Quality bars? | docs/27 (+ 23) |
| Operations? | docs/28, 32 |
