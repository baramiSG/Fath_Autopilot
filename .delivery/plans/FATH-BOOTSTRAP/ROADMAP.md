# FATH_AUTOPILOT — Delivery Roadmap (Weeks 1–6)

**Artifact type:** Operational roadmap state (NOT new project authority)
**Project:** FATH_AUTOPILOT · **Task:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT (Claude Fable 5, 1M, Thinking ON, Max)
**Baseline:** `ae5a4ea7db30d9ba243e29c98424702f5e0fb7a1` · **Amendment commit:** `234a24d9e012710352d35aa5b1314a6395614945`

> **WARNING.** This roadmap decomposes authoritative scope into governed increments. It creates no requirements and implies no completion: nothing on it is done until a candidate is independently reviewed, merged, and evidenced. Authoritative scope lives in `docs/` (AMENDMENT-001 `docs/33` at top of precedence, then `docs/24`, then the corpus). Weeks 2–6 entries are COARSE and MUST be re-decomposed into bounded task contracts by the planner at each week's task-planning time, re-reading the cited canonical sections. Requirement IDs reference `REQUIREMENTS_TRACEABILITY.json` (derived internal identifiers).

## Governance applying to every task

- One bounded task at a time; task branch `task/TASK-XXX-<slug>`; immutable candidate SHA; independent implementation review binds to that exact SHA; merge only after gates (control-plane constitution §7–9, review policy §16–21).
- Every task ends Confirm, Validate, Test, with recorded evidence.
- **CI status (FATH-PR-006/FATH-P2-004):** all task CI runs are SHA-bound test evidence, NOT trusted verification. **GATE-SETUP (explicit roadmap item, owner: Salim; REQUIRED BEFORE ANY MERGE — TASK-001 included):** branch protection on `main`, trusted exact-identity CI verification, and receipts, each mechanically verified per BOOTSTRAP_PLAN §9. Until verified: trusted gates NOT_CONFIGURED, branch protection NOT_VERIFIED (BUILD_STATE), and every review-approved candidate halts at REVIEW_APPROVED — NOT merge-eligible. There is no review-plus-controller substitute. Implementation and independent review may proceed in parallel with GATE-SETUP; merging may not.
- AMENDMENT-001 verifier checklist applies to **every** task from TASK-001 onward: no A100 assumption; no Azure OpenAI SDK/endpoint/deployment/env; provider-agnostic LLM client only (Week 2+); RTX 5090 workstation sizing for local GPU work; budget/trust-boundary mediation of all frontier-LLM calls.

## Week 1 — Foundation slice (bounded tasks; sequenced)

Scope authority: docs/18 (build scope), docs/23 (Week-1 done criteria as corrected by docs/24 §1), docs/17 (Week 1), docs/24, docs/33. **Week-1 LLM posture (PROPOSED — BOOTSTRAP_PLAN §4.4, FATH-PR-004):** zero reasoning-model calls in Week 1; Canvas v0 uses a deterministic spec producer behind a producer interface, with the doc-07 validate → retry-once → fallback pipeline fully implemented and fixture-tested; the model producer plugs in behind the Week-2 provider-agnostic LLM client. Not a necessity claim — doc 14 permits 200 daily-ingestion LLM calls and docs 07/18 define model-produced UI specs.

| Task | Title | Depends on | Requirements (traceability) |
|---|---|---|---|
| **TASK-001** | Repository foundation: doc-16-conformant scaffold, uv env, config, Postgres 16+AGE+pgvector & Redis 7 compose, Alembic baseline, source-registry **schema only** (no seed data — FA-OPEN-020), SHA-bound CI evidence | — (first implementation task; plan approved with this bootstrap) | FA-REQ-W1-001 (schema portion)/002 (schema portion), W1-018/019/020, CP-001/002, AM constraints (no Azure artifact) |
| TASK-002 | Hash-chained append-only audit log (doc-15 formula; doc-24 §8 Pattern A in-transaction writes) | 001 | FA-REQ-W1-007 |
| TASK-003 | Raw Archive store + MinIO object storage + session duplicate guard (doc-24 §2 insert-policy matrix) | 001, 002 | FA-REQ-W1-005/006, INV-002 |
| TASK-004 | Redis Streams event bus + EventEnvelope + consumer groups + DLQ + idempotency_keys + durable event outbox | 001, 002 | FA-REQ-W1-008/009 |
| TASK-005 | Trust boundary: UntrustedBlob, sanitizer, injection_patterns.yaml, delimiter escaping, quarantine ≥ 0.85, fixtures | 001 | FA-REQ-W1-010 |
| TASK-006 | Registry seed data (`config/sources_seed.yaml` + loader, 16 records) + `source_onboarding_checklists` (doc-29 DDL) + Tier-0 activation evidence + Access Guard (doc-03 rules 1–10) + registry service; every decision persisted; non-active denied. **GATED on FA-OPEN-020 (Salim-approved seed value table + Tier-0 onboarding checklists) — dispatch without it is BLOCKED_FOR_SALIM** | 001, 002, 004; FA-OPEN-020 | FA-REQ-W1-001 (seed portion)/002/003/004 |
| TASK-007 | Qatar Open Data API connector (metadata-first, archive, hash, events, failure table) | 003, 004, 005, 006, 009 | FA-REQ-W1-011/012 |
| TASK-008 | World Bank + GDELT connectors (same contract) | 007 (pattern established) | FA-REQ-W1-011/012 |
| TASK-009 | Redis budget counters, reserve/refund with rollback, circuit breakers, doc-14 defaults | 001 | FA-REQ-W1-013 |
| TASK-010 | Minimal Fact Store slice: facts table with full FactStatus (incl. quarantined) from first fact migration, provenance-mandatory insert path, transition map + audit | 001, 002 | FA-REQ-W1-014, INV-002 |
| TASK-011 | Prefect 3 schedules + LangGraph graphs: hourly source_check_heartbeat (zero LLM calls), daily ingestion graph, state snapshots, idempotent nodes, resume | 003–010 | FA-REQ-W1-015 |
| TASK-012 | FastAPI backend: SSE from Redis Streams, UI-spec generation restricted to v0 approved components, backend Pydantic validation, retry-then-fallback | 004, 005 | FA-REQ-W1-016 |
| TASK-013 | Next.js + TypeScript Canvas v0: Zod validation, component registry (7 v0 components), first-screen rule, rejection behavior | 012 | FA-REQ-W1-016 |
| TASK-014 | Week-1 integration smoke + evidence run against docs/23 done criteria (as corrected); recorded evidence | all above | FA-REQ-W1-003/017 |

Gate to Week 2: doc-27 Week-1 phase gate + doc-23 done criteria evidenced; all candidates independently reviewed and merged.

## Week 2 — Parsing, embeddings, LLM client, extractors, graph (COARSE — re-decompose)

Authority: docs/31 (steps 1–7), 17 (Week 2), 10, 21, 22, 24 §3/§6, 27 (extraction gates), **33**. Requirements: FA-REQ-W2-001/002/003, AM-001, AM-002, EVAL-001.

- **W2-LLM-CLIENT (NEW, first — AMENDMENT-001):** provider-agnostic frontier-LLM client with configurable model routing, budget/breaker mediation, trust-boundary-delimited prompts, model-call logging. Precedes all extractor tasks. Module placement ADR required (FA-OPEN-004 fold-in). Dispatch requires FA-OPEN-009 credentials, else BLOCKED_FOR_SALIM.
- Parser pipeline (ParsedArtifact, chunking) and BGE-M3 embedding baseline (1024-dim; stub path allowed per doc 31; real serving sized for RTX 5090 workstation per AMENDMENT-001 — sizing re-derivation in that task's plan).
- pgvector HNSW table + hybrid retrieval interface; embedding-namespace ADR (FA-OPEN-003); module-path ADR (FA-OPEN-004).
- Extractors (economic indicator, trade flow, legal constraint v0, policy claim) via the LLM client; Fact Store full implementation; golden extraction sets + `make eval` start (doc 27).
- Entity Resolver; Knowledge Graph Builder (relational canonical + AGE mirror, ARTICLE_PART_OF_LAW, FDI_TARGETS_COUNTRY); EarlyFactCard/EvidenceGraphExplorer; Week-2 smoke (≥3 facts, ≥5 nodes, ≥3 edges).

## Week 3 — Proactive intelligence (COARSE — re-decompose)

Authority: docs/17 (Week 3), 10 (Connection Agent), 08, 13, 27. Requirements: FA-REQ-W3-001. Change Detector; Anomaly Miner; Connection Agent (0.75/0.55 thresholds); Coverage Auditor v0; investigation proposal workflow; Canvas investigation cards; ≥3 unprompted investigations. Canvas-registry ADR if InvestigationCard delta becomes material (FA-OPEN-001).

## Week 4 — Hypotheses and simulation (COARSE — re-decompose)

Authority: docs/17 (Week 4), 26, 24 §10, **33** (simulation/batch on workstation). Requirements: FA-REQ-W4-001, AM-002. Hypothesis Store full; Policy Genome Generator; Scenario Runner v0 (template-based only, 4 templates, LHS n=200, ranking + dominance w/ novelty ≥9.0); no-network sandbox with resource caps sized for the workstation; Causal Skeptic; ScenarioTournamentView.

## Week 5 — Validation, defense, calibration, auth (COARSE — re-decompose)

Authority: docs/17 (Week 5), 11, 24 §9, 12, 04 (store 5), 25, 27, **33**. Requirements: FA-REQ-W5-001. Sanad five-chain validator (EvidenceBundle mandatory); Source-Poisoning Detector; Belief Calibration Store; Run Replay; Source Integrity Radar; RBAC/approvals backend-enforced (dev token; production provider OPEN per AMENDMENT-001 — FA-OPEN-011). Grounding-similarity ADR (FA-OPEN-002).

## Week 6 — Insights, briefing, demo (COARSE — re-decompose)

Authority: docs/17 (Week 6), 01 (success criteria), 08, 32. Requirements: FA-REQ-W6-001, OPS-001 (pre-continuous-operation checks). Insight Corpus (Sanad-gated promotion); weekly Briefing Composer; Approval Marshal + human review; final Canvas demo flow; six-week success criteria evidence; doc-32 readiness + kill criteria before any continuous operation.

## Open items carried on this roadmap

FA-OPEN-001 (Canvas registry, W3/W6 human-approved ADR) · FA-OPEN-002 (similarity threshold, W5 ADR) · FA-OPEN-003 (namespaces, W2 ADR) · FA-OPEN-004 (module paths + LLM-client placement, W2 human-approved ADR per doc 23) · FA-OPEN-009 (frontier-LLM API credentials — Salim, before W2 LLM tasks) · FA-OPEN-010 (RTX 5090 workstation connection + sizing re-derivation — Salim/W2+W4 plans) · FA-OPEN-011 (production auth provider — OPEN per docs/33; Salim, production phase) · FA-OPEN-012 (Comtrade key — Tier-1 activation) · FA-OPEN-018 (mandatory provider designation — reserved to Salim) · FA-OPEN-019 (production secrets/object-store hosting — Salim, production phase) · **FA-OPEN-020 (seed value table + Tier-0 onboarding checklists — Salim; MATERIAL: gates TASK-006 and therefore TASK-007/008/014)** · FA-OPEN-021 (dual-identifier source-identity model, UUID PK + unique TEXT slug — DERIVED reconciliation, reviewer confirms; BOOTSTRAP_PLAN §7.4) · **GATE-SETUP (Salim; MATERIAL: gates every merge, including TASK-001's)**. None blocks TASK-001 implementation or review; FA-OPEN-020 gates the Week-1 activation chain; GATE-SETUP gates all merges.
