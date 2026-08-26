# 24 — Final Implementation Corrections and Non-Negotiable Invariants

## Purpose

This document resolves the remaining inconsistencies found after reviewing the full build documentation. It is not a conceptual addendum. It is an implementation correction layer that the Reasoner, Engineer, and Verifier must treat as authoritative.

If a prior document conflicts with this one, **this document wins** until the earlier document is patched.

## Corrections summary

| Area | Correction |
|---|---|
| Week 1 sources | Week 1 active sources are Qatar Open Data, World Bank, and GDELT only. Al Meezan remains in the registry but is `manual_review_required` until Access Guard approval is completed. |
| Canvas components | `RawArchiveRecordCard` is a first-class component and must be included in backend and frontend registries. |
| Raw Archive idempotency | Raw Archive is append-only, but crawlers must avoid duplicate inserts for the same `source_id + url + content_hash + crawl_session_id`. New content versions always insert new rows. |
| Fact lifecycle | `quarantined` is part of the Fact status enum from the first migration, not added later. |
| Knowledge graph | Add missing `ARTICLE_PART_OF_LAW` and `FDI_TARGETS_COUNTRY` edge types. |
| Trust boundary | `UntrustedBlob` is immutable. Truncation or quarantine must produce a copied instance via `model_copy(update=...)`; do not mutate. |
| Audit logging | Do not use async `create_task` inside SQLAlchemy event listeners. Use explicit service writes or an audit outbox table. |
| Sanad source grounding | Cosine similarity alone is not enough. Every source-grounding pass must produce an Evidence Bundle with quote/table/page spans. |
| Simulation | First implementation uses deterministic simulation templates. No LLM-generated simulation code executes in production until sandbox certification passes. |
| Budget | Budget counters must support both reservation and refund. Partial reservations across scopes must be rolled back on any failure. |
| Human approval | Approval authority is RBAC-controlled. A UI button is not sufficient; the backend must enforce roles. |

---

## 1. Week 1 source correction

Previous drafts mention an Al Meezan legal collector in Week 1. That is too early because Al Meezan is marked `manual_review` in the source registry.

### Correct Week 1 active set

```text
qatar_open_data
world_bank
gdelt
```

### Correct Week 1 inactive-but-defined set

```text
al_meezan      status = candidate_manual_review
qcb            status = candidate_manual_review
qse            status = candidate_manual_review
invest_qatar   status = candidate_manual_review
```

### Source status enum

Add this to the `sources` table and Pydantic model:

```python
SourceStatus = Literal[
    "candidate",
    "candidate_manual_review",
    "approved_inactive",
    "active",
    "suspended",
    "quarantined",
    "retired",
]
```

```sql
ALTER TABLE sources ADD COLUMN status TEXT NOT NULL DEFAULT 'candidate'
CHECK (status IN (
    'candidate',
    'candidate_manual_review',
    'approved_inactive',
    'active',
    'suspended',
    'quarantined',
    'retired'
));
```

### Access Guard rule

```python
if source.status != "active":
    return AccessDecision(
        decision="deny",
        reason="manual_review_required" if source.status == "candidate_manual_review" else "source_not_active",
        notes=f"Source {source.source_id} is not active: {source.status}",
    )
```

This prevents accidental early crawling of legal or report-heavy sites.

---

## 2. Raw Archive idempotency correction

Raw Archive is immutable, but crawling must not generate duplicate rows from repeated checks within the same crawl session.

### Insert policy

```text
Same source_id + url + content_hash + crawl_session_id  → do not insert duplicate
Same source_id + url + content_hash + different session → insert only if configured `record_repeated_seen=true`; default false
Same source_id + url + different content_hash            → insert new row
Same source_id + different url + same content_hash        → insert new row, because provenance differs
```

### Unique index

```sql
CREATE UNIQUE INDEX uq_raw_archive_session_duplicate_guard
ON raw_archive_records(source_id, url, content_hash, crawl_session_id);
```

### Crawler behavior

```python
async def store_raw_artifact(...):
    try:
        return await raw_archive.insert(record)
    except UniqueViolation:
        return await raw_archive.fetch_existing(
            source_id=source_id,
            url=url,
            content_hash=content_hash,
            crawl_session_id=crawl_session_id,
        )
```

Do not update an existing raw record. The crawler may return the existing record ID for idempotency.

---

## 3. Fact lifecycle correction

`quarantined` must be present from migration 1. Source-poisoning can fire before later migrations, so quarantine cannot be an afterthought.

### Correct status enum

```python
FactStatus = Literal[
    "extracted",
    "corroborated",
    "superseded",
    "quarantined",
    "rejected",
]
```

### Status transition rules

```text
extracted     → corroborated
extracted     → superseded
extracted     → quarantined
corroborated  → superseded
corroborated  → quarantined
quarantined   → extracted       only by human release, with audit row
quarantined   → rejected        by human or poisoning detector finalization
superseded    → terminal
rejected      → terminal
```

### Transition function

```python
ALLOWED_FACT_TRANSITIONS: dict[str, set[str]] = {
    "extracted": {"corroborated", "superseded", "quarantined", "rejected"},
    "corroborated": {"superseded", "quarantined", "rejected"},
    "quarantined": {"extracted", "rejected"},
    "superseded": set(),
    "rejected": set(),
}
```

Every transition must write an audit row.

---

## 4. Canvas component correction

`RawArchiveRecordCard` is used by Week 1 but was missing in some component registries. It must be included.

### Backend enum

```python
ComponentName = Literal[
    "WhatFathWantsToInvestigate",
    "AutopilotPulse",
    "InvestigationQueue",
    "SourceUpdateCard",
    "AccessGuardDecisionCard",
    "RawArchiveRecordCard",
    "EarlyFactCard",
    "EvidenceGraphExplorer",
    "PolicyGenomeCard",
    "ScenarioTournamentView",
    "SanadValidationCard",
    "SourceIntegrityRadar",
    "BeliefCalibrationPanel",
    "RunReplay",
    "ApprovalGateCard",
]
```

### Payload model

```python
class RawArchiveRecordCardPayload(BaseModel):
    raw_archive_id: UUID
    source_id: str
    source_name: str
    url: str
    fetched_at: datetime
    content_hash: str
    content_type: str
    content_size_bytes: int
    fetch_method: Literal["api", "download", "crawl", "manual"]
    sanitization_status: Literal["pending", "completed", "failed", "quarantined"]
    follow_up_events: list[UUID] = Field(default_factory=list)
```

### Event mapping

```python
EVENT_TO_COMPONENTS["RawArchiveAdded"] = ["RawArchiveRecordCard", "AutopilotPulse"]
```

---

## 5. Event payload correction

`RawArchiveAddedPayload` must include `content_hash` and `crawl_session_id` so downstream consumers can deduplicate and correlate.

```python
class RawArchiveAddedPayload(BaseModel):
    raw_archive_id: UUID
    source_id: str
    url: str
    content_hash: str
    content_type: str
    content_size_bytes: int
    fetched_at: datetime
    crawl_session_id: UUID
    fetch_method: Literal["api", "download", "crawl", "manual"]
```

---

## 6. Knowledge graph correction

The graph queries reference edges not defined in the graph schema. Add these two edge types.

### `ARTICLE_PART_OF_LAW`

| From | To | Properties |
|---|---|---|
| `LawArticle` | `Law` | `article_number: str` |

### `FDI_TARGETS_COUNTRY`

| From | To | Properties |
|---|---|---|
| `FDIProject` | `Country` | `target_role: Literal["host_country"]` |

### Corrected FDI gap logic

The FDI gap query must compare Qatar against benchmark countries by host country, not by source country.

```cypher
MATCH (s:Sector)<-[:FDI_TARGETS_SECTOR]-(p:FDIProject)-[:FDI_TARGETS_COUNTRY]->(host:Country)
WHERE host.iso3 IN $benchmark_countries
WITH s, host, count(p) AS benchmark_count
MATCH (s)<-[:FDI_TARGETS_SECTOR]-(p2:FDIProject)-[:FDI_TARGETS_COUNTRY]->(qa:Country {iso3: 'QAT'})
WITH s, sum(benchmark_count) AS benchmark_total, count(p2) AS qatar_count
WHERE benchmark_total > qatar_count * 2
RETURN s, benchmark_total, qatar_count, (benchmark_total - qatar_count) AS gap
ORDER BY gap DESC
LIMIT 25
```

---

## 7. Trust boundary correction

`UntrustedBlob` is immutable. Do not mutate `content_truncated` or `quarantined` in place.

### Correct truncation pattern

```python
def truncate_blob(blob: UntrustedBlob, max_chars: int) -> UntrustedBlob:
    if len(blob.content) <= max_chars:
        return blob
    return blob.model_copy(update={
        "content": blob.content[:max_chars],
        "content_truncated": True,
    })
```

### Delimiter escaping

Before placing content into the data block, escape delimiter-like text.

```python
DELIMITER_ESCAPES = {
    "<<<UNTRUSTED_DATA_BLOCK_START": "＜＜＜UNTRUSTED_DATA_BLOCK_START",
    "<<<UNTRUSTED_DATA_BLOCK_END": "＜＜＜UNTRUSTED_DATA_BLOCK_END",
    "<<<SYSTEM": "＜＜＜SYSTEM",
    "<<<TRUSTED": "＜＜＜TRUSTED",
}

def escape_delimiters(text: str) -> str:
    for src, dst in DELIMITER_ESCAPES.items():
        text = text.replace(src, dst)
    return text
```

The delimiter spoofing test must assert that spoofed delimiters cannot close the block early.

---

## 8. Audit logging correction

Do not create async tasks inside SQLAlchemy event listeners. They can run outside the transaction boundary, fail silently, or race with rollback.

### Correct pattern A: explicit domain service audit write

Every write service returns both the row mutation and the audit row in the same transaction.

```python
async with session.begin():
    fact = await fact_repo.insert_fact(session, fact_model)
    await audit_repo.append_in_transaction(
        session=session,
        actor_kind="agent",
        actor_id=extractor_id,
        event_category="memory_writes",
        event_type="fact_inserted",
        target_kind="fact",
        target_id=str(fact.id),
        payload={...},
    )
```

### Correct pattern B: audit outbox

If high throughput is needed, write an outbox row inside the transaction and have a separate worker convert outbox rows into hash-chain audit rows.

```sql
CREATE TABLE audit_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_kind TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    event_category TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_kind TEXT,
    target_id TEXT,
    correlation_id UUID,
    causation_id UUID,
    payload JSONB NOT NULL,
    processed_at TIMESTAMPTZ,
    processing_error TEXT
);

CREATE INDEX idx_audit_outbox_unprocessed
ON audit_outbox(created_at)
WHERE processed_at IS NULL;
```

For Week 1, use **Pattern A** for simplicity.

---

## 9. Sanad source-grounding correction

Source grounding must not rely on cosine similarity alone. Cosine similarity is retrieval; it is not verification.

### Evidence Bundle schema

```python
class EvidenceSpan(BaseModel):
    raw_archive_id: UUID
    source_id: str
    source_url: str
    page_number: int | None = None
    table_id: str | None = None
    char_start: int | None = None
    char_end: int | None = None
    quote: str
    quote_hash: str

class EvidenceBundle(BaseModel):
    bundle_id: UUID
    hypothesis_id: UUID
    supporting_spans: list[EvidenceSpan]
    contradicting_spans: list[EvidenceSpan] = Field(default_factory=list)
    retrieval_query: str
    retrieval_top_k: int
    reranker_model: str
    created_at: datetime
```

### Updated source-grounding algorithm

```text
1. Retrieve candidate chunks through hybrid retrieval.
2. Rerank candidates.
3. Extract specific quote/table/page spans.
4. Build EvidenceBundle.
5. Ask GPT-5.4 only whether each span supports, contradicts, or is unrelated to the hypothesis.
6. Pass only if at least 3 independent supporting spans exist from at least 2 independent sources OR 1 primary source + 2 corroborating public sources.
```

### Independence rule

Two spans are independent only if they do not share:

```text
same source_id
same raw_archive_id
same citation chain parent
same ownership_bloc, if source metadata exists
```

---

## 10. Simulation correction

Do not execute arbitrary LLM-generated simulation code in the first production build.

### Approved first-build simulation mode

```text
template-based simulation only
parameterized model definitions only
pre-reviewed Python modules only
Docker sandbox with no network
CPU/GPU/time limits enforced
reproducible random seed recorded
```

LLM-generated code may be used only in a research notebook outside the production path until the sandbox certification checklist in `26_SIMULATION_SANDBOX_AND_POLICY_TOURNAMENT.md` passes.

---

## 11. Budget rollback correction

When the LLM client reserves budgets across multiple scopes, failure at any scope must refund prior reservations.

```python
reserved: list[tuple[Scope, str, ResourceKind, int]] = []
try:
    for scope, key, resource, amount in reservations:
        await enforcer.reserve(scope, key, resource, amount)
        reserved.append((scope, key, resource, amount))
except BudgetExceeded:
    for scope, key, resource, amount in reversed(reserved):
        await enforcer.refund(scope, key, resource, amount)
    raise
```

Add `refund()` to `BudgetEnforcer` and test it.

---

## 12. Approval correction

The UI cannot be the authority for approval. Backend RBAC must enforce it.

```python
class ApprovalPolicy(BaseModel):
    action_kind: str
    required_role: str
    min_approval_count: int
    expires_after_hours: int
    requires_reason: bool = True
```

Examples:

```yaml
publish_tier_b_insight:
  required_role: analyst
  min_approval_count: 1
  expires_after_hours: 168
  requires_reason: true

release_quarantine:
  required_role: security_reviewer
  min_approval_count: 1
  expires_after_hours: 168
  requires_reason: true

external_action:
  required_role: admin
  min_approval_count: 2
  expires_after_hours: 24
  requires_reason: true
```

See `25_AUTH_RBAC_AND_APPROVALS.md` for full implementation.

## Verifier checklist for this correction document

A build is non-compliant if any of these are false:

1. `RawArchiveRecordCard` exists in backend and frontend registries.
2. `RawArchiveAddedPayload` includes `content_hash` and `crawl_session_id`.
3. Week 1 active source registry contains only Qatar Open Data, World Bank, and GDELT.
4. `FactStatus` includes `quarantined` in the first migration.
5. Graph schema includes `ARTICLE_PART_OF_LAW` and `FDI_TARGETS_COUNTRY`.
6. TrustBoundary uses immutable copy semantics for truncation/quarantine.
7. Audit writes do not rely on async SQLAlchemy event listeners.
8. Sanad source grounding creates Evidence Bundles with spans.
9. Simulation runner executes only pre-reviewed templates in the first production path.
10. Backend RBAC enforces approvals.
