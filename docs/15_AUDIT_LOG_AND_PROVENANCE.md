# 15 — Audit Log and Provenance

## Purpose

Every important action must be auditable. The audit log must be tamper-evident and append-only.

## Implementation decision

Use an append-only Postgres table with hash-chained rows.

## Audit row schema

```python
class AuditActionType(str, Enum):
    SOURCE_ACCESSED = "source_accessed"
    RAW_ARCHIVED = "raw_archived"
    CONTENT_SANITIZED = "content_sanitized"
    FACT_EXTRACTED = "fact_extracted"
    FACT_VALIDATED = "fact_validated"
    GRAPH_UPDATED = "graph_updated"
    HYPOTHESIS_CREATED = "hypothesis_created"
    INSIGHT_PROMOTED = "insight_promoted"
    BELIEF_CREATED = "belief_created"
    BELIEF_CALIBRATED = "belief_calibrated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECIDED = "approval_decided"
    BUDGET_BREACHED = "budget_breached"
    SOURCE_QUARANTINED = "source_quarantined"
    CONFIG_CHANGED = "config_changed"

class AuditLogRecord(BaseModel):
    audit_id: UUID
    sequence_no: int
    occurred_at: datetime
    actor_type: Literal["agent", "user", "system"]
    actor_id: str
    action_type: AuditActionType
    target_object_type: str
    target_object_id: Optional[UUID]
    run_id: Optional[UUID]
    event_id: Optional[UUID]
    payload_hash_sha256: str
    payload_canonical_json: dict[str, Any]
    previous_row_hash_sha256: str
    row_hash_sha256: str
```

## Hash chain

Row hash calculation:

```text
row_hash = sha256(
    previous_row_hash_sha256
    + canonical_json(payload)
    + actor_id
    + action_type
    + target_object_id
    + occurred_at_iso
)
```

Use canonical JSON with sorted keys and stable formatting.

## SQL table

```sql
CREATE TABLE audit_log (
    audit_id UUID PRIMARY KEY,
    sequence_no BIGSERIAL UNIQUE,
    occurred_at TIMESTAMPTZ NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_object_type TEXT NOT NULL,
    target_object_id UUID,
    run_id UUID,
    event_id UUID,
    payload_hash_sha256 TEXT NOT NULL,
    payload_canonical_json JSONB NOT NULL,
    previous_row_hash_sha256 TEXT NOT NULL,
    row_hash_sha256 TEXT NOT NULL UNIQUE
);

CREATE INDEX idx_audit_time ON audit_log(occurred_at DESC);
CREATE INDEX idx_audit_target ON audit_log(target_object_type, target_object_id);
CREATE INDEX idx_audit_run ON audit_log(run_id);
CREATE INDEX idx_audit_action ON audit_log(action_type);
```

## Append-only enforcement

Application rule:

- no update,
- no delete,
- insert only.

Database enforcement:

- revoke update/delete permissions from app role,
- optionally add triggers that raise on update/delete.

## Provenance rule

Every Fact Store record must point to:

```text
source_id
raw_id
evidence_span
extraction_method
extractor_version
created_at
```

Every Insight Corpus record must point to:

```text
hypothesis_id(s)
fact_id(s)
raw_id(s)
sanad_validation_id
scenario_result_id(s), if applicable
```

Every UI card must point to:

```text
event_id(s)
run_id
source object IDs
```

## Run replay

Run Replay reconstructs:

```text
source checked
access decision
raw archive
sanitization
fact extraction
graph update
connection found
hypothesis generated
simulation
Sanad validation
insight promotion
UI rendering
```

No insight should be accepted if it cannot be replayed.
