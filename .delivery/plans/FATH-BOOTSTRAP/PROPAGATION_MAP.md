# AMENDMENT-002 Source-Identity Propagation Map (full-corpus sweep)

**Artifact type:** Planning material — binding propagation map required by `docs/34_AMENDMENT_002_SOURCE_IDENTITY.md` §12. NOT new project authority: every row derives from the cited canonical text plus AMENDMENT-002; where they conflict, AMENDMENT-002 wins (docs/34 Precedence).
**Project:** FATH_AUTOPILOT · **Scope:** FATH-BOOTSTRAP (plan V5) · **Role:** CHIEF_ARCHITECT / TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max — inherited runtime)
**Row count:** 84 mapped rows (PM-A1..A6, B1..B5, C1..C7, D1..D15, E1..E6, F1..F3, G1..G6, H1..H4, I1..I2, J1..J8, K1..K5, L1..L5, M1..M5, N1..N7). Count corrected and provenance/graph surfaces added per FATH-V4-007/009.
**Amendment:** docs/34, sha256 `0edb5245999e88382eab1c8a0f9679f45e60d3cd680903f3b56f3a3768dd9b99`, commit `af00923853e0234da403231258c822b949e9da00`, HUMAN-APPROVED (Salim, 2026-08-27).

**Method (§12 compliance):** the complete corpus (docs 00–33 + README; combined file reference-only) was read in full and additionally swept mechanically for every occurrence of `source_id`, `source_ids`, `sources(`, `slug`, `source_slug`, `source_name`, `source_registry`, `source_refs`, "source object", the doc-24/30 slug literals, and source-keyed dict/label structures — including a dedicated provenance/graph sweep of docs 15/27/31/32 (FATH-V4-007). Every surface is mapped individually below with its citation. **No blanket `str`-type assumption is used anywhere** — each `str`-typed surface is individually classified. Where authority does not establish a surface's semantics, the row records an explicit OPEN item instead of an implicit mapping.

**Universal rules being propagated (all SPECIFIED by docs/34):**

- **R1 (§§1–2):** `source_registry` is the single canonical source table; no `sources` table; `sources(id)` references map to `source_registry(source_id)`; `source_id UUID PRIMARY KEY`, immutable.
- **R2 (§3):** `source_registry.slug TEXT NOT NULL UNIQUE`; stable after activation except audited migration.
- **R3 (§4):** `source_id` ALWAYS = canonical UUID; `slug`/`source_slug` ALWAYS = readable identifier; `source_name` display-only; no contract may use `source_id` to carry a slug.
- **R4 (§5):** internal Pydantic/domain models retain `source_id: UUID`; readable identifier travels as separate `source_slug: str`.
- **R5 (§6):** ALL persisted relational source FKs reference `source_registry(source_id)`; never `slug` absent an explicit human-approved ADR.
- **R6 (§7):** doc-29 `source_id TEXT ... REFERENCES sources(id)` DDL superseded → UUID referencing `source_registry(source_id)`.
- **R7 (§8):** human-authored YAML/catalog definitions key on `slug:`; UUID assigned at registry-record creation.
- **R8 (§9):** transport (events, APIs, Redis, UI/TypeScript) `source_id` strings are serialized UUIDs; readable ids travel separately as `source_slug`; payloads may carry `source_id` + `source_slug` + `source_name` with distinct semantics.
- **R9 (§10):** existing UUID contracts (docs 03/04/05/07/21 and other UUID-bearing source contracts) survive.
- **R10 (§11):** textual identifiers in docs 24/29/30 and related catalogs survive with semantic role `slug`/`source_slug`.

Classification legend: **SPECIFIED** = the amendment (or surviving canonical text) directly requires it. **DERIVED** = logically necessary application of R1–R10 to a surface the amendment does not name verbatim; derivation stated. **PROPOSED** = reversible engineering choice. Owning task = where the surface is first implemented.

---

## A. Tables (§12: table)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-A1 | `source_registry` table | docs/03 Indices (lines 175–178); docs/22 §2 list | Single canonical source table; created in migration 0001 | SPECIFIED (R1) | TASK-001 |
| PM-A2 | `sources` table (doc-24 §1 `ALTER TABLE sources ...`; doc-29 `REFERENCES sources(id)` twice) | docs/24 line 65; docs/29 lines 82, 223 | **No `sources` table exists.** Doc-24 §1 status column + CHECK applies to `source_registry`; doc-29 parent references map to `source_registry(source_id)` | SPECIFIED (R1, R6) | TASK-001 (status column); TASK-006 (doc-29 tables) |
| PM-A3 | `source_onboarding_checklists` | docs/29 lines 81–105 | Created per doc-29 with identity column corrected per PM-C3 | SPECIFIED (R6) | TASK-006 |
| PM-A4 | `source_terms_snapshots` | docs/29 lines 221–230 | Created per doc-29 with identity column corrected per PM-C4 | SPECIFIED (R6) | TASK-006+ |
| PM-A5 | `document_chunks`, `embeddings` | docs/21 §6 DDL | Survive verbatim (already UUID) | SPECIFIED (R9) | Week 2 |
| PM-A6 | Future tables in docs/22 §2 list that will carry source references (`source_poisoning_alerts`, `llm_usage`, etc. — schemas defined at owning tasks) | docs/22 §2 | Any persisted source FK → `source_registry(source_id)` | SPECIFIED (R5, catch-all §6 "any other persisted FK representing source identity") | owning tasks |

## B. Columns (§12: column)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-B1 | `source_registry.source_id` | docs/03 line 74; docs/34 §2 | `UUID PRIMARY KEY`, immutable canonical identity. **Immutability mechanically enforced in TASK-001**: BEFORE UPDATE trigger `trg_source_registry_source_id_immutable` raising on any `source_id` change, with structural check + negative test (TASK-001_PLAN §6.0/A4 ix–x; FATH-V4-001) | SPECIFIED invariant (R1); trigger mechanism PROPOSED | TASK-001 |
| PM-B2 | `source_registry.slug` | docs/34 §3 (column name given by the amendment itself) | `TEXT NOT NULL UNIQUE`; houses the docs-24 §1 / 29 / 30 textual identifiers (PM-M1..M3). **Post-activation stability (§3) has a tested owning task (FATH-V4-001): TASK-006** — the task introducing activation MUST implement mechanical enforcement (trigger forbidding `slug` UPDATE on non-candidate rows except through its defined audited-migration path) with negative tests, as a binding acceptance obligation (ROADMAP TASK-006) | SPECIFIED (R2, R10); enforcement obligation binding | TASK-001 (column); TASK-006 (stability enforcement) |
| PM-B3 | `source_registry.status` + CHECK (7 values, default `'candidate'`) | docs/24 §1 lines 52–75 (stated against `sources`) | Applies to `source_registry` per R1 | SPECIFIED (doc 24 §1 + R1) | TASK-001 |
| PM-B4 | All other `SourceRegistryRecord` fields as columns (name, source_class, reliability_tier, base_url, …, metadata) | docs/03 lines 73–104 | Columns per doc-03 contract; **complete PG type/nullability/default/constraint mapping pre-bound in TASK-001_PLAN §6.0** (FATH-V4-002) — the fixture transcribes the plan; mapping choices classified there (DERIVED rules; BIGINT for `max_bytes_per_cycle` PROPOSED) | SPECIFIED fields; DERIVED/PROPOSED type mapping, plan-bound | TASK-001 |
| PM-B5 | `source_name` anywhere (docs 06/07/21/24/30 payload/props fields) | e.g. docs/06 line 115; docs/07 lines 108/122/136/269; docs/21 line 149; docs/24 lines 209; docs/30 line 88 | Display-only; never an identity key | SPECIFIED (R3) | all owning tasks |

## C. Foreign keys (§12: foreign key)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-C1 | `raw_archive.source_id → source_registry.source_id` | docs/04 line 195 (+ record contract line 148) | Survives verbatim (UUID) | SPECIFIED (R5, R9) | TASK-003 |
| PM-C2 | `access_decisions.source_id` (AccessDecision context; doc-03 index line 179) | docs/03 lines 122, 179; docs/34 §6 "Access Guard decisions" | UUID FK → `source_registry(source_id)` | SPECIFIED (R5) | TASK-006 |
| PM-C3 | `source_onboarding_checklists.source_id TEXT PRIMARY KEY REFERENCES sources(id)` | docs/29 line 82 | **Superseded:** `source_id UUID PRIMARY KEY REFERENCES source_registry(source_id)` | SPECIFIED (R6; §6 "onboarding checklists") | TASK-006 |
| PM-C4 | `source_terms_snapshots.source_id TEXT NOT NULL REFERENCES sources(id)` | docs/29 line 223 | **Superseded:** `source_id UUID NOT NULL REFERENCES source_registry(source_id)` | SPECIFIED (R6; §6 "terms snapshots") | TASK-006+ |
| PM-C5 | `document_chunks.source_id UUID NOT NULL REFERENCES source_registry(source_id)`; same in `embeddings` | docs/21 lines 106, 124 | Survive verbatim | SPECIFIED (R9) | Week 2 |
| PM-C6 | doc-24 §2 session duplicate-guard unique index `(source_id, url, content_hash, crawl_session_id)` on raw archive | docs/24 lines 107–110 | `source_id` therein = UUID FK column of PM-C1 (table name maps to `raw_archive` per FA-OPEN-006) | SPECIFIED (R3) | TASK-003 |
| PM-C7 | Prohibition: any FK targeting `source_registry(slug)` | docs/34 §6 | Forbidden absent explicit human-approved ADR; TASK-001 oracle checks none exists | SPECIFIED (R5) | TASK-001 oracle + all tasks |

## D. Pydantic/domain models (§12: Pydantic model)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-D1 | `SourceRegistryRecord.source_id: UUID` | docs/03 line 74 | Survives; model additionally carries `slug: str` (R2) and doc-24 §1 `status` | SPECIFIED (R9 + R2 + doc 24 §1) | TASK-001 |
| PM-D2 | `AccessDecision.source_id: UUID` | docs/03 line 122 | Survives | SPECIFIED (R9) | TASK-006 |
| PM-D3 | `SourcePointer.source_id: UUID` (shared helper used across stores) | docs/04 line 72 | Survives | SPECIFIED (R9) | TASK-003+ |
| PM-D4 | `RawArchiveRecord.source_id: UUID` | docs/04 line 148 | Survives | SPECIFIED (R9) | TASK-003 |
| PM-D5 | `UntrustedBlob.source_id: UUID`; `mark_untrusted(..., source_id: UUID, ...)` | docs/05 lines 60, 82 | Survive | SPECIFIED (R9) | TASK-005 |
| PM-D6 | `CrawlRequest.source_id: UUID`; `CrawlResult.source_id: UUID` | docs/09 lines 21, 31 | Survive | SPECIFIED (R9) | TASK-007/008 |
| PM-D7 | `RetrievalHit.source_id: Optional[UUID]` | docs/10 line 89 | Survives | SPECIFIED (R9) | Week 2 |
| PM-D8 | `DocumentChunk.source_id: UUID`; `EmbeddingRecord.source_id: UUID`; `RetrievedChunk.source_id: UUID` | docs/21 lines 47, 69, 146 | Survive | SPECIFIED (R9) | Week 2 |
| PM-D9 | `ClaimCandidate.source_id: UUID`; `ClaimCluster.source_ids: list[UUID]` | docs/12 lines 29, 48 | Survive | SPECIFIED (R9) | Week 5 |
| PM-D10 | `SourceOnboardingChecklist.source_id: str` | docs/29 line 56 | **Superseded:** field carries the UUID identity (`source_id: UUID`); where a readable id is needed the model exposes separate `source_slug: str` | SPECIFIED (R3, R4, R6) | TASK-006 |
| PM-D11 | `SourceRiskScore.source_id: str` | docs/29 line 180 | **Superseded:** `source_id: UUID`; readable id as separate `source_slug` where needed | SPECIFIED (R3, R4) | Week 5 (source risk scoring) |
| PM-D12 | doc-24 §9 `EvidenceSpan.source_id: str` (EvidenceBundle) | docs/24 line 381 | `source_id` = UUID (serialized where JSON); readable id as `source_slug` if needed | SPECIFIED (R3, R8; §6 "audit/evidence records") | Week 5 |
| PM-D13 | doc-24 §9 independence rule "same source_id" | docs/24 line 417 | UUID comparison | SPECIFIED (R3) | Week 5 |
| PM-D14 | doc-24 §1 Access Guard snippet `f"Source {source.source_id} is not active"` | docs/24 line 84 | Interpolated `source_id` = UUID; a readable message may additionally include `source_slug` | SPECIFIED (R3); message wording free | TASK-006 |
| PM-D15 | `BeliefCalibrationRecord.source_reliability_snapshot: dict[str, float]`; `source_reliability_adjustments: dict[str, float]` | docs/04 lines 545, 556 | Key semantics not defined by doc 04. As persisted per-source references in a memory store, keys are serialized UUID `source_id` (R3 + §6 "memory-store references" + R8 JSON-string rule). Derivation: these dicts persist source-keyed values; §4 forbids a `source`-identity key that is secretly a slug; §9 fixes the JSON string form as serialized UUID | DERIVED (from R3/R5/R8) | Week 5/6 (Belief Calibration) |

## E. Event payloads (§12: event payload)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-E1 | `SourceUpdateDetectedPayload.source_id: str` | docs/06 line 114 | Serialized UUID; `source_name` stays display; `source_slug` MAY be added where useful | SPECIFIED (R8) | TASK-004/011 |
| PM-E2 | `AccessGuardDecisionPayload.source_id: str` | docs/06 line 127 | Serialized UUID | SPECIFIED (R8) | TASK-004/006 |
| PM-E3 | `RawArchiveAddedPayload.source_id: str` (doc 06 + doc 24 §5) | docs/06 line 141; docs/24 line 235 | Serialized UUID | SPECIFIED (R8) | TASK-004/007 |
| PM-E4 | `PoisoningSignalDetectedPayload.affected_source_ids: list[str]` | docs/06 line 231 | List of serialized UUIDs | SPECIFIED (R8) | Week 5 |
| PM-E5 | `FactExtractedPayload` (no source_id field; `source_url` only) | docs/06 lines 154–162 | Reviewed — no identity field; no change | reviewed, no impact | Week 2 |
| PM-E6 | All other doc-06 payloads (Investigation/PolicyGenome/Scenario/Sanad/Approval/Budget) | docs/06 catalog | Reviewed field-by-field — no source-identity fields | reviewed, no impact | — |

## F. API contracts (§12: API contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-F1 | `api/routes/sources.py` (and any route carrying a source identifier in path/query/body) | docs/16 line 111 | JSON `source_id` values = serialized UUID; readable filter/lookup parameters exposed as `source_slug` | SPECIFIED (R8) | TASK-012 |
| PM-F2 | doc-25 `ApprovalRequest.target_id: str` / `target_kind` where the target is a source (e.g. `activate_source`) | docs/25 lines 169–170, 196–197 | Generic field: when `target_kind` designates a source, `target_id` carries the serialized UUID `source_id`. Derivation: R3 fixes what a source identity is; the generic transport string form follows R8 | DERIVED (from R3/R8) | Week 5 |
| PM-F3 | SSE stream payloads (doc 25 filtering; doc 02 SSE) | docs/25 SSE section; docs/02 | Same as the event payloads they carry (PM-E1..E4) | SPECIFIED (R8) | TASK-012 |

## G. UI contracts (§12: UI contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-G1 | `SourceUpdateCardProps.source_id: UUID` (Python) | docs/07 line 107 | Survives (UUID) | SPECIFIED (R9) | TASK-012 |
| PM-G2 | TypeScript `SourceUpdateCardProps.source_id: string` | docs/07 line 395 | The TS string is the serialized UUID — it does NOT become the slug; a readable id, if shown, travels as a separate `source_slug` prop added per R8 | SPECIFIED (R8) | TASK-013 |
| PM-G3 | `SourceIntegrityItem.source_id: UUID` | docs/07 line 268 | Survives | SPECIFIED (R9) | Week 5 |
| PM-G4 | doc-24 §4 `RawArchiveRecordCardPayload.source_id: str` | docs/24 line 208 | Serialized UUID | SPECIFIED (R8) | TASK-012/013 |
| PM-G5 | `AccessGuardDecisionCardProps`, `RawArchiveRecordCardProps`, `EarlyFactCardProps` (`source_name` only, no source_id) | docs/07 lines 120–158 | Reviewed — `source_name` display-only per R3; no identity change | reviewed, no impact | TASK-012/013 |
| PM-G6 | Frontend Zod schemas for the above | docs/07 TS interfaces; docs/27 Canvas gates | `source_id` validated as UUID-format string; `source_slug` separate readable string where added | SPECIFIED (R8) | TASK-013 |

## H. Crawler contracts (§12: crawler contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-H1 | `CrawlRequest.source_id: UUID`, `CrawlResult.source_id: UUID` | docs/09 lines 21, 31 | Survive | SPECIFIED (R9) | TASK-007/008 |
| PM-H2 | doc-24 §2 insert-policy matrix rows "Same source_id + …" | docs/24 lines 99–102 | `source_id` = UUID | SPECIFIED (R3) | TASK-003/007 |
| PM-H3 | doc-24 §2 `fetch_existing(source_id=source_id, ...)` | docs/24 line 120 | UUID argument | SPECIFIED (R3) | TASK-003/007 |
| PM-H4 | doc-30 YAML `crawler_class:` | docs/30 line 108 | Reviewed — module path, not identity; no change | reviewed, no impact | TASK-006 |

## I. Retrieval contracts (§12: retrieval contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-I1 | `RetrievalHit.source_id: Optional[UUID]` (doc 10); `RetrievedChunk.source_id: UUID` + `source_name: str` (doc 21) | docs/10 line 89; docs/21 lines 146, 149 | Survive; `source_name` display-only | SPECIFIED (R9, R3) | Week 2 |
| PM-I2 | Source-deduplication / `max_chunks_per_source` retrieval defaults | docs/21 §8 | Per-source grouping keys on UUID `source_id` | SPECIFIED (R3) | Week 2 |

## J. Provenance/audit contracts (§12: provenance contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-J1 | doc-15 provenance rule: every Fact Store record points to `source_id` | docs/15 line 109 | UUID | SPECIFIED (R3) | TASK-010, Week 2 |
| PM-J2 | `AuditLogRecord.target_object_id: Optional[UUID]` when the target is a source | docs/15 line 39 | UUID `source_id` (already UUID-typed; consistent) | SPECIFIED (R9) | TASK-002+ |
| PM-J3 | doc-28 structured-log field `source_id` | docs/28 line 177 | Serialized UUID; a parallel readable field, if added, is `source_slug` | SPECIFIED (R8) | all tasks |
| PM-J4 | doc-28 Prometheus label `fath_raw_archive_records_total{source_id}` | docs/28 line 159 | Label value = serialized UUID; a readable label, if added, is a separate `source_slug` label | SPECIFIED (R8) | Week 2+ (metrics) |
| PM-J5 | doc-28 runbook `quarantine_source.py --source-id SOURCE` | docs/28 line 302 | `--source-id` takes the serialized UUID; owning task may add a separate `--source-slug` convenience lookup (resolved through the registry) | SPECIFIED (R3); convenience flag PROPOSED | Week 5+ (ops scripts) |
| PM-J6 | doc-15 UI-card provenance rule: "Every UI card must point to: event_id(s), run_id, **source object IDs**" | docs/15 lines 127–133 | Referent SET not defined by authority (registry sources vs the evidence objects the card renders). Identity FORM is settled: every candidate referent (source_registry, facts, raw archive, insights) is UUID-keyed (R3/R9), serialized per R8 in UI transport. Referent-set definition = **OPEN (FA-OPEN-022 companion: FA-OPEN-023)**, owned by the Canvas provenance task | FORM DERIVED (R3/R8/R9); referent set OPEN (FA-OPEN-023) | Week 3 (Canvas provenance) |
| PM-J7 | Graph node/edge `source_refs` — docs 27/31/32 require every graph node/edge to carry non-empty `source_refs`; doc-22 §3 canonical DDL defines `provenance_fact_ids UUID[]` and NO `source_refs` element | docs/27 lines 138–139; docs/31 lines 161–163; docs/32 line 51; docs/22 §3 DDL | Structural referent ambiguous: (a) `source_refs` = the fact-provenance chain (`provenance_fact_ids`, transitively resolving fact → raw → `source_id`), or (b) a direct persisted source-reference element. **OPEN (FA-OPEN-022)**, owned by the Week-2 Knowledge-Graph-Builder task plan. Binding constraint either way: any DIRECT persisted source reference MUST be UUID(s) → `source_registry(source_id)` (R5); any new column beyond the doc-22 DDL requires a human-approved ADR (doc-23 anti-drift) | Constraint SPECIFIED (R5); structure OPEN (FA-OPEN-022) | Week 2 (Knowledge Graph Builder) |
| PM-J8 | doc-15 audit event types `SOURCE_ACCESSED`, `SOURCE_QUARANTINED` | docs/15 lines 15, 28 | Event-type names, not identity carriers; the acting-on-source identity travels in `AuditLogRecord.target_object_id` (UUID — PM-J2) | reviewed, no identity change | TASK-002+ |

## K. Poisoning/integrity contracts (§12: poisoning/integrity contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-K1 | `ClaimCandidate.source_id: UUID`; `ClaimCluster.source_ids: list[UUID]` | docs/12 lines 29, 48 | Survive | SPECIFIED (R9) | Week 5 |
| PM-K2 | `PoisoningSignalDetectedPayload.affected_source_ids: list[str]` | docs/06 line 231 | Serialized UUIDs (= PM-E4) | SPECIFIED (R8) | Week 5 |
| PM-K3 | `SourceIntegrityItem.source_id: UUID` (radar UI) | docs/07 line 268 | Survives (= PM-G3) | SPECIFIED (R9) | Week 5 |
| PM-K4 | `source_poisoning_alerts` table (schema at owning task) | docs/22 §2 list | Persisted source FKs → `source_registry(source_id)` | SPECIFIED (R5) | Week 5 |
| PM-K5 | `independence_group`/`independence_groups` fields | docs/03 line 95; docs/12 line 49 | Reviewed — group labels, not source identity; no change | reviewed, no impact | — |

## L. Onboarding/compliance contracts (§12: onboarding/compliance contract)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-L1 | `SourceOnboardingChecklist` model + DDL | docs/29 lines 55–105 | PM-D10 + PM-C3: UUID identity; readable id as `source_slug` where needed; parent = `source_registry(source_id)` | SPECIFIED (R6) | TASK-006 |
| PM-L2 | `source_terms_snapshots` DDL | docs/29 lines 221–230 | PM-C4 | SPECIFIED (R6) | TASK-006+ |
| PM-L3 | `SourceRiskScore.source_id: str` | docs/29 line 180 | PM-D11 | SPECIFIED (R3/R4) | Week 5 |
| PM-L4 | doc-29 verifier item 1 "YAML definition exists" | docs/29 line 244 | YAML keys on `slug:` (PM-M4) | SPECIFIED (R7) | TASK-006 |
| PM-L5 | doc-29 `source_terms_snapshots.raw_archive_id ... REFERENCES raw_archive_records(id)` | docs/29 line 227 | Table name maps to `raw_archive(raw_id)` per FA-OPEN-006 physical-naming resolution (not an identity change; recorded for completeness) | DERIVED (FA-OPEN-006) | TASK-006+ |

## M. Source YAML/catalog definitions (§12: source YAML/catalog definition)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-M1 | doc-24 §1 Week-1 sets: `qatar_open_data`, `world_bank`, `gdelt`; `al_meezan`, `qcb`, `qse`, `invest_qatar` | docs/24 lines 33–46 | These literals are **slugs** (`source_registry.slug` values) | SPECIFIED (R10) | TASK-006 |
| PM-M2 | doc-30 tier lists (Tier 0–3 textual ids) | docs/30 lines 18–82 | Slugs | SPECIFIED (R10) | TASK-006+ |
| PM-M3 | doc-30 candidate template key `source_id: candidate_source_id` | docs/30 line 87 | **Superseded key name:** human-authored definitions use `slug: candidate_slug`; UUID `source_id` is assigned at registry-record creation, never authored in YAML | SPECIFIED (R7) | TASK-006 |
| PM-M4 | `config/sources_seed.yaml` (doc 16 layout; content = TASK-006, values gated on FA-OPEN-020) | docs/16 line 13 | Keys on `slug:`; seed VALUES remain gated on FA-OPEN-020 (Salim) — the amendment resolves identity semantics, NOT the missing base URLs/tiers/rate limits | SPECIFIED (R7); values OPEN (FA-OPEN-020) | TASK-006 |
| PM-M5 | docs/03 "Initial registry seeds" 16 display names | docs/03 lines 151–168 | Display names (`name` column / `source_name`); identity keys are the slugs (PM-M1/M2); values gated on FA-OPEN-020 | SPECIFIED (R3, R10) | TASK-006 |

## N. Other source-identity representations (swept; not named verbatim in §12 but covered by its catch-all intent)

| # | Surface | Citation | Mapping | Class | Owning task |
|---|---|---|---|---|---|
| PM-N1 | doc-14 Redis budget key `budget:{scope}:{scope_id}:{limit_name}`, example `budget:source:almeezan:max_pages` | docs/14 lines 25, 32 | §9 names Redis explicitly: a Redis textual representation of source identity is the serialized UUID. Application: the per-source `{scope_id}` = serialized UUID `source_id`; the doc-14 `almeezan` example survives as illustration only | Rule SPECIFIED (R8); application to `scope_id` DERIVED | TASK-009 |
| PM-N2 | AGE graph node label `Source` (node properties carrying registry identity) | docs/22 §4 | Persisted `source_id` property = serialized UUID (JSON property per R8); `slug` may be stored as separate readable property | DERIVED (R3/R8) | Week 2 |
| PM-N3 | doc-27 golden dataset file names (`qatar_open_data_sample.json`, …) and doc-05 fixture name (`clean_qatar_open_data_sample.json`) | docs/27 lines 29–33; docs/05 line 193 | File names use readable slugs — naming convention, not an identity contract; record content that carries `source_id` fields follows the owning contract's mapping above | reviewed, no identity impact | Week 2+ / TASK-005 |
| PM-N4 | doc-05 prompt header `UNTRUSTED_DATA_START ... source_id={source_id} ...` | docs/05 line 116 | Interpolates `UntrustedBlob.source_id` (UUID) — rendered as serialized UUID | SPECIFIED (R8/R9) | TASK-005 |
| PM-N5 | doc-03 `subscription_name`, doc-30 `ownership_bloc`, `jurisdiction` | docs/03 line 84; docs/30 lines 109–110 | Reviewed — descriptive metadata, not identity; no change | reviewed, no impact | — |
| PM-N6 | doc-27 golden layout `golden/sources/`, eval-harness steps "Verify source registry active sources" / "Source registry loads", extraction failure taxonomy "wrong source reference" | docs/27 lines 28, 102, 239, 279 | Directory/step naming and failure labels — not identity contracts. Registry lookups in the eval harness resolve readable slugs → UUID `source_id` through the registry (R3); golden record CONTENT carrying `source_id` fields follows the owning contract's mapping (PM-N3) | reviewed, no identity change; lookups DERIVED (R3) | Week 2+ (eval harness) |
| PM-N7 | doc-32 readiness checklist source rows: registry contains only approved sources; each active source has onboarding checklist / rate limits / robots-terms review; every fact has `raw_archive_refs` | docs/32 lines 26–29, 50; docs/06 line 160 | Checklist assertions over registry records and onboarding artifacts — identity semantics per PM-A1/L1 (UUID `source_id`, slug readable); `raw_archive_refs` is `list[UUID]` of raw-archive ids (already UUID, doc 06), not a source-identity surface | reviewed, no identity change | Week 6 (readiness) |

---

## Consequences bound into plan V5

1. **TASK-001** creates `source_registry` exactly per PM-A1/B1/B2/B3/B4 with the complete expected schema pre-bound in TASK-001_PLAN §6.0, and its §13 oracle (A4) proves: UUID `source_id` PK **with immutability trigger + negative test**; `slug TEXT NOT NULL UNIQUE`; no `sources` table; FK count in `public` = 0 (positive assertion); exact pre-bound defaults/types/constraints/indexes; exact table set.
2. **TASK-006** implements PM-C2/C3, PM-D10/D14, PM-M1–M5 (values still gated on FA-OPEN-020) **and the PM-B2 slug-stability enforcement obligation (trigger + audited-migration path + negative tests — FATH-V4-001)**.
3. **Event/UI/API tasks** (TASK-004/007/008/012/013) implement PM-E1–E4, PM-F1/F3, PM-G2/G4/G6 — transport `source_id` = serialized UUID, `source_slug` separate.
4. **The V3 rule "event/UI `source_id: str` carries the slug" is dead.** It was the FATH-P3-001 defect and is replaced by R8 everywhere.
5. **The V3 proposal "doc-29 FKs → `source_registry(slug)`" is dead.** Replaced by R6 (UUID → `source_registry(source_id)`).
6. Any future need to key a persisted FK on `slug` requires an explicit human-approved ADR (R5) — stop condition, not a design option.
7. **Two source-reference surfaces have genuinely ambiguous authority semantics and are recorded OPEN rather than implicitly mapped (FATH-V4-007):** graph `source_refs` (PM-J7 → FA-OPEN-022, owned by the Week-2 Knowledge-Graph-Builder plan) and doc-15 UI-card "source object IDs" (PM-J6 → FA-OPEN-023, owned by the Week-3 Canvas provenance plan). Both carry the binding constraint that any direct persisted source reference is UUID → `source_registry(source_id)`.
