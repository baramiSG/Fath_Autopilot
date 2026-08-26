# 23 — Implementation Coverage Checklist

This file maps the technical critique into concrete documentation coverage. Use it before starting implementation to confirm that no agent or LLM-coder session is operating from conceptual intent alone.

## Coverage map

| Critique item | Status | Primary docs |
|---|---:|---|
| Full Pydantic memory-store schemas | Covered | `04_MEMORY_STORE_SCHEMAS.md` |
| Trust boundary implementation contract | Covered | `05_TRUST_BOUNDARY_AND_SANITIZATION.md` |
| Locked stack decisions | Covered | `02_ARCHITECTURE_DECISIONS.md` |
| Event bus taxonomy and schemas | Covered | `06_EVENT_BUS_CONTRACT.md` |
| Fath Canvas component contracts + TS interfaces | Covered | `07_FATH_CANVAS_GENERATIVE_UI.md` |
| Sanad five-chain algorithm specs | Covered | `11_SANAD_VALIDATION_SPEC.md` |
| Source-poisoning detection algorithms | Covered | `12_SOURCE_POISONING_AND_NARRATIVE_DEFENSE.md` |
| Connection Agent mechanism | Covered | `10_EMBEDDING_RETRIEVAL_AND_CONNECTIONS.md` |
| Heartbeat workflow implementation | Covered | `13_WORKFLOWS_HEARTBEATS_AND_STATE.md` |
| Budget enforcement implementation | Covered | `14_BUDGET_RATE_LIMIT_AND_CIRCUIT_BREAKERS.md` |
| Audit log implementation | Covered | `15_AUDIT_LOG_AND_PROVENANCE.md` |
| Embedding pipeline details | Covered | `10_EMBEDDING_RETRIEVAL_AND_CONNECTIONS.md`, `21_DETAILED_EMBEDDING_PIPELINE_APPENDIX.md` |
| Folder structure and module boundaries | Covered | `16_PROJECT_STRUCTURE_AND_MODULE_BOUNDARIES.md` |
| First build prompt / LLM coder kickoff | Covered | `18_WEEK1_AI_CODER_KICKOFF.md` |

## Implementation readiness gates

Before code generation begins, the Reasoner must confirm:

1. The build uses only public/open/legally accessible sources.
2. No ministry-private data, LMIS, QNWIS, or internal datasets are used.
3. Crawlers do not import or call the LLM router.
4. All external content is represented as `UntrustedBlob` before any LLM use.
5. The event schema is used for every agent output that should be visible or auditable.
6. Fath Canvas renders only approved component specs.
7. Raw Archive and Fact Store are implemented before Hypothesis Store.
8. Budget counters exist before any scheduled crawler runs.
9. Audit logging exists before production-like autonomous runs.
10. The Week 1 system can show at least one proactive UI event without manual prompting.

## Week 1 done criteria

Week 1 is complete only when:

- Source Registry table exists.
- Access Guard decisions are persisted.
- Qatar Open Data connector can fetch and archive at least one approved dataset.
- World Bank connector can fetch and archive at least one indicator response.
- Al Meezan collector can archive an approved legal page or manually supplied public legal artifact under conservative rules.
- Raw Archive stores immutable raw material with hashes.
- Fact Store can store at least one extracted fact with provenance.
- Trust Boundary has passing injection tests.
- Event outbox stores source/crawl/raw/fact events.
- Fath Canvas renders Autopilot Pulse and Investigation Queue from event specs.
- Budget Manager blocks or defers at least one synthetic budget breach in tests.
- Audit Log hash-chain verification passes.

## Anti-drift rule

If an LLM coder proposes a new schema, module path, event type, source access method, or UI component not defined in this folder, it must produce an ADR-style note and receive human approval before implementation.

---

# Final v3 coverage additions

The final review added the following implementation documents. These are mandatory build context after v3.

| File | Added coverage |
|---|---|
| `24_FINAL_IMPLEMENTATION_CORRECTIONS.md` | Resolves final inconsistencies: Week 1 source set, RawArchive idempotency, fact quarantine status, Canvas component mismatch, KG edge gaps, trust-boundary immutability, audit logging pattern, EvidenceBundle requirement, simulation-code restriction, approval RBAC. |
| `25_AUTH_RBAC_AND_APPROVALS.md` | Production authentication, roles, permissions, approval state machine, backend enforcement, SSE filtering. |
| `26_SIMULATION_SANDBOX_AND_POLICY_TOURNAMENT.md` | Template-based simulation, no-network sandbox, scoring formula, dominance rule, reproducibility, LLM-generated code certification gate. |
| `27_EVALUATION_AND_QUALITY_GATES.md` | Golden datasets, extraction/retrieval/graph/Sanad/Canvas/security quality thresholds, phase gates. |
| `28_OPERATIONS_BACKUP_RESTORE_AND_DR.md` | Backups, restore drills, RPO/RTO, migrations, metrics, incidents, runbooks. |
| `29_SOURCE_LICENSING_COMPLIANCE_AND_ONBOARDING.md` | Source onboarding, licensing, terms, PII avoidance, paid-source review, source-risk scoring. |
| `30_SEED_SOURCE_CATALOG_AND_PRIORITY_MAP.md` | Qatar source backlog, activation order, source-to-use-case map, country portability. |
| `31_WEEK2_KICKOFF_EXTRACTORS_AND_GRAPH.md` | Week 2 build protocol for parsed artifacts, chunks, fact extraction, entity resolution, and graph. |
| `32_PRODUCTION_READINESS_CHECKLIST.md` | Final continuous-operation readiness, demo readiness, and kill criteria. |

## Additional final-build checks

A build is not accepted unless:

1. `RawArchiveRecordCard` exists and renders.
2. Week 1 active sources are exactly: `qatar_open_data`, `world_bank`, `gdelt`.
3. Al Meezan is inactive until manual source review passes.
4. `quarantined` exists in `FactStatus` from the first fact migration.
5. `ARTICLE_PART_OF_LAW` and `FDI_TARGETS_COUNTRY` exist in graph schema.
6. Source grounding produces Evidence Bundles with quote/table/page spans.
7. RBAC prevents unauthorized approval through direct API calls.
8. Simulation runner uses reviewed templates only in production.
9. Backup and restore drill pass before continuous operation.
10. `make eval` exists and produces an EvalReport.
