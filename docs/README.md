# Fath Autopilot Documentation Folder

**Fath Autopilot** is a proactive sovereign economic reasoning system designed to use public and legally accessible data to discover, test, validate, and brief high-impact economic and policy opportunities.

The first proof target is Qatar. The architecture is country-portable: only the source registry, legal corpus, benchmark set, and institutional map change when the system is adapted to another sovereign context.

## Core product definition

Fath Autopilot continuously scans public laws, open datasets, trade flows, macro indicators, financial disclosures, investment signals, and regional policy moves. It builds a living economic knowledge graph, proposes its own investigations, generates policy genomes, stress-tests them through scenarios, validates findings through Sanad, calibrates its beliefs against outcomes, and presents its work through a controlled generative UI called **Fath Canvas**.

## Operating principle

> **Autonomous in research. Restricted in action.**

The system may autonomously collect approved public data, update memory, generate hypotheses, run simulations, validate findings, and produce internal briefings. It may not send external messages, submit forms, access private systems, write outside approved workspaces, use unrestricted shell access, or perform external actions without explicit human approval.

## Documentation map

| File | Purpose |
|---|---|
| `00_MASTER_BUILD_CONTEXT.md` | One-file context for an LLM coder. Read this first. |
| `01_PRODUCT_AND_SCOPE.md` | Product thesis, Qatar first use case, success criteria, exclusions. |
| `02_ARCHITECTURE_DECISIONS.md` | Locked technology decisions. No option lists. |
| `03_SOURCE_REGISTRY_AND_ACCESS_POLICY.md` | Approved source registry, access guard, source scoring. |
| `04_MEMORY_STORE_SCHEMAS.md` | Pydantic-level specifications for the five memory stores. |
| `05_TRUST_BOUNDARY_AND_SANITIZATION.md` | Untrusted content contract, prompt assembly, injection fixtures. |
| `06_EVENT_BUS_CONTRACT.md` | Event taxonomy, payload schemas, delivery semantics, dead letters. |
| `07_FATH_CANVAS_GENERATIVE_UI.md` | Controlled generative UI contracts, backend schemas, TypeScript interfaces. |
| `08_AGENT_ROLE_SPECIFICATIONS.md` | Agent responsibilities, inputs, outputs, boundaries. |
| `09_CRAWLER_AND_INGESTION_SPEC.md` | API, legal, report, news, and benchmark crawler implementation specs. |
| `10_EMBEDDING_RETRIEVAL_AND_CONNECTIONS.md` | Embeddings, chunking, retrieval, Connection Agent algorithm. |
| `11_SANAD_VALIDATION_SPEC.md` | Sanad five-chain validator algorithms and schemas. |
| `12_SOURCE_POISONING_AND_NARRATIVE_DEFENSE.md` | Source poisoning, citation loops, claim clustering, narrative defense. |
| `13_WORKFLOWS_HEARTBEATS_AND_STATE.md` | Prefect schedules, LangGraph workflow specs, state persistence. |
| `14_BUDGET_RATE_LIMIT_AND_CIRCUIT_BREAKERS.md` | Budget counters, Redis keys, token counting, circuit breakers. |
| `15_AUDIT_LOG_AND_PROVENANCE.md` | Tamper-evident audit log, provenance rules, hash chain schema. |
| `16_PROJECT_STRUCTURE_AND_MODULE_BOUNDARIES.md` | Canonical repository layout and module responsibilities. |
| `17_BUILD_PLAN_AND_VERIFICATION.md` | Six-week build sequence and verification checklist. |
| `18_WEEK1_AI_CODER_KICKOFF.md` | Step 1 Reasoner prompt for the first build slice. |
| `19_RISK_REGISTER.md` | Operational, security, data, and product risks. |
| `20_TERMINOLOGY.md` | Terms, controlled vocabulary, and naming conventions. |
| `21_DETAILED_EMBEDDING_PIPELINE_APPENDIX.md` | Detailed embedding/chunking/pgvector retrieval contracts. |
| `22_DATABASE_SCHEMA_AND_INDICES_APPENDIX.md` | Database extensions, graph tables, indices, and integrity rules. |
| `23_IMPLEMENTATION_COVERAGE_CHECKLIST.md` | Checklist mapping critique items to implementation docs and Week 1 done criteria. |

| `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` | Final corrections and invariants that override earlier conflicts. |
| `25_AUTH_RBAC_AND_APPROVALS.md` | Authentication, role-based access control, backend approval enforcement. |
| `26_SIMULATION_SANDBOX_AND_POLICY_TOURNAMENT.md` | Safe simulation templates, sandboxing, tournament scoring, reproducibility. |
| `27_EVALUATION_AND_QUALITY_GATES.md` | Golden datasets, evaluation metrics, regression gates, phase thresholds. |
| `28_OPERATIONS_BACKUP_RESTORE_AND_DR.md` | Backup, restore, disaster recovery, observability, incidents. |
| `29_SOURCE_LICENSING_COMPLIANCE_AND_ONBOARDING.md` | Source terms, licensing, PII avoidance, paid-source review, activation workflow. |
| `30_SEED_SOURCE_CATALOG_AND_PRIORITY_MAP.md` | Qatar source backlog, source priority tiers, cross-country portability map. |
| `31_WEEK2_KICKOFF_EXTRACTORS_AND_GRAPH.md` | Week 2 build instruction for extractors and the knowledge graph. |
| `32_PRODUCTION_READINESS_CHECKLIST.md` | Continuous-operation readiness checklist and kill criteria. |


## First implementation slice

The first slice is deliberately small but visible:

1. Source Scout
2. Access Guard
3. Qatar Open Data connector
4. World Bank connector
5. GDELT connector
6. Raw Archive
7. TrustBoundary + Sanitizer
8. Event Bus
9. Audit Log
10. Fath Canvas v0 with Autopilot Pulse, SourceUpdateCard, AccessGuardDecisionCard, and RawArchiveRecordCard

Al Meezan is defined in the registry but remains inactive until manual source review passes.

The first visible behavior should be:

> “Fath checked approved public sources, detected changes, archived raw material, extracted early facts, proposed investigations, and rendered them in the UI without waiting for a user query.”

## Build constraints

- Public and legally accessible data only.
- No LMIS, no ministry-private data, no QNWIS data for the first proof.
- Azure OpenAI GPT-5.4 only for reasoning.
- 8×A100 VM is used for embeddings, extraction, reranking, OCR, simulation, and batch processing.
- No external actions without approval.
- No arbitrary browser automation in the first slice.
- No unrestricted shell access for agents.

## Intended reader

This folder is written for:

- the builder,
- an LLM coding agent,
- a verifier,
- a government security reviewer,
- and a future technical reviewer who needs to understand contracts rather than intentions.


## v3 final reading rule

For any implementation session, load `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` after the original module docs. If it conflicts with an earlier file, file 24 wins. For any production or demo preparation session, also load files 25–32.
