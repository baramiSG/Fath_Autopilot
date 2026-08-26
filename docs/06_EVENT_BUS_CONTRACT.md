# 06 — Event Bus Contract

## Purpose

The event bus makes agent actions visible, auditable, replayable, and renderable in Fath Canvas. Fath uses **Redis Streams** for operational events. Audit integrity remains in the separate hash-chained Postgres audit log.

## Implementation decision

Use Redis Streams with consumer groups.

```text
Producers → Redis Streams → consumer groups → UI Orchestrator / Audit Logger / agent consumers
```

No Kafka in v1. No ephemeral Pub/Sub. No Postgres event bus.

## Delivery semantics

| Property | Decision |
|---|---|
| Delivery | At least once |
| Ordering | Guaranteed within one stream only |
| Cross-stream ordering | Not guaranteed |
| Consumer groups | Required |
| Idempotency | Required for every consumer |
| Retry | Event retry counter; reclaim pending after timeout |
| Dead letters | After 3 failed attempts move to `<stream>:dlq` |
| Replay | Re-consume stream by ID or from stored cursor |
| Retention | Streams retained for 90 days by default; audit log retained indefinitely |

## Stream names

```text
events:sources
events:crawl
events:archive
events:safety
events:facts
events:graph
events:reasoning
events:simulation
events:validation
events:insights
events:calibration
events:approval
events:budget
events:run
```

## Event envelope

```python
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class EventEnvelope(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    schema_version: int = 1
    occurred_at: datetime
    producer_agent: str
    correlation_id: UUID | None = None
    causation_id: UUID | None = None
    trace_id: str | None = None
    autonomy_level_required: int = Field(default=1, ge=1, le=5)
    payload: dict
```

## Event type catalog

| Stream | Event type | Producer | Primary consumers | Canvas component |
|---|---|---|---|---|
| `events:sources` | `SourceUpdateDetected` | Source Scout | Crawlers, UI | `SourceUpdateCard` |
| `events:sources` | `AccessGuardDecision` | Access Guard | Crawlers, UI, Audit | `AccessGuardDecisionCard` |
| `events:crawl` | `CrawlStarted` | Crawler | UI | `AutopilotPulse` |
| `events:crawl` | `CrawlCompleted` | Crawler | UI | `AutopilotPulse` |
| `events:crawl` | `CrawlFailed` | Crawler | UI, Audit | `AutopilotPulse` |
| `events:archive` | `RawArchiveAdded` | Crawler | Sanitizer, UI | `RawArchiveRecordCard` |
| `events:safety` | `SanitizationCompleted` | Sanitizer | Extractors | internal |
| `events:safety` | `InjectionDetected` | Sanitizer | UI, Audit | `AutopilotPulse` |
| `events:safety` | `PoisoningSignalDetected` | Poisoning Detector | UI, Audit | `SourceIntegrityRadar` |
| `events:facts` | `FactExtracted` | Extractor | Graph Builder, UI | `EarlyFactCard` |
| `events:facts` | `FactSuperseded` | Extractor | Graph Builder, UI | `EarlyFactCard` |
| `events:graph` | `GraphEdgeAdded` | Graph Builder | Connection Agent, UI | `EvidenceGraphExplorer` |
| `events:reasoning` | `AnomalyDetected` | Anomaly Miner | Hypothesis Generator, UI | `AutopilotPulse` |
| `events:reasoning` | `ConnectionFound` | Connection Agent | Hypothesis Generator, UI | `AutopilotPulse` |
| `events:reasoning` | `CoverageGapIdentified` | Coverage Auditor | Hypothesis Generator, UI | `InvestigationQueue` |
| `events:reasoning` | `InvestigationProposed` | Hypothesis Generator | UI | `WhatFathWantsToInvestigate` |
| `events:reasoning` | `HypothesisGenerated` | Hypothesis Generator | Policy Genome Generator | internal |
| `events:reasoning` | `PolicyGenomeProposed` | Policy Genome Generator | Scenario Runner, UI | `PolicyGenomeCard` |
| `events:simulation` | `ScenarioRunStarted` | Scenario Runner | UI | `ScenarioTournamentView` |
| `events:simulation` | `ScenarioRunCompleted` | Scenario Runner | Sanad, UI | `ScenarioTournamentView` |
| `events:validation` | `SanadChainStarted` | Sanad | UI | `SanadValidationCard` |
| `events:validation` | `SanadChainCompleted` | Sanad | UI, Insight Corpus | `SanadValidationCard` |
| `events:insights` | `InsightPublished` | Sanad | Briefing, UI | `PolicyGenomeCard` |
| `events:calibration` | `PredictionMade` | Calibration | UI | `BeliefCalibrationPanel` |
| `events:calibration` | `PredictionResolved` | Calibration | UI | `BeliefCalibrationPanel` |
| `events:approval` | `ApprovalRequested` | Approval Marshal | UI | `ApprovalGateCard` |
| `events:approval` | `ApprovalGranted` | Approval Marshal | originating workflow | internal |
| `events:approval` | `ApprovalRejected` | Approval Marshal | originating workflow | internal |
| `events:budget` | `BudgetWarning` | Budget Enforcer | UI, Audit | `AutopilotPulse` |
| `events:budget` | `BudgetExceeded` | Budget Enforcer | UI, Audit | `AutopilotPulse` |
| `events:run` | `HeartbeatStarted` | Workflow | UI | `AutopilotPulse` |
| `events:run` | `HeartbeatCompleted` | Workflow | UI | `AutopilotPulse` |
| `events:run` | `HeartbeatFailed` | Workflow | UI, Audit | `AutopilotPulse` |

## Payload schemas

### `SourceUpdateDetected`

```python
class SourceUpdateDetectedPayload(BaseModel):
    source_id: str
    source_name: str
    detection_method: Literal["etag", "last_modified", "content_hash", "feed_diff"]
    previous_marker: str | None
    current_marker: str
    detected_at: datetime
    estimated_change_significance: float = Field(ge=0, le=1)
```

### `AccessGuardDecision`

```python
class AccessGuardDecisionPayload(BaseModel):
    source_id: str
    target_url: str
    decision: Literal["allow", "defer", "deny"]
    reason: str
    retry_after_seconds: int | None = None
    requested_at: datetime
    notes: str = ""
```

### `RawArchiveAdded`

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

### `FactExtracted`

```python
class FactExtractedPayload(BaseModel):
    fact_id: UUID
    claim: str
    claim_type: str
    extractor_id: str
    confidence: float = Field(ge=0, le=1)
    raw_archive_refs: list[UUID]
    source_url: str
```

### `InvestigationProposed`

```python
class InvestigationProposedPayload(BaseModel):
    investigation_id: UUID
    title: str
    rationale: str
    triggering_signals: list[dict]
    expected_relevance_score: float = Field(ge=0, le=1)
    al_muhasibi_novelty_score: float = Field(ge=0, le=10)
    proposed_research_tasks: list[str]
    estimated_runtime_minutes: int
```

### `PolicyGenomeProposed`

```python
class PolicyGenomeProposedPayload(BaseModel):
    policy_genome_id: UUID
    hypothesis_id: UUID
    target_sector: str
    title: str
    summary: str
    evidence_chain_fact_ids: list[UUID]
    estimated_impact_low_usd_billions: float | None = None
    estimated_impact_high_usd_billions: float | None = None
    implementation_difficulty: Literal["low", "medium", "high"]
    novelty_score: float
```

### `ScenarioRunCompleted`

```python
class ScenarioRunCompletedPayload(BaseModel):
    scenario_run_id: UUID
    policy_genome_id: UUID
    candidates_generated: int
    candidates_rejected: int
    candidates_simulated: int
    candidates_shortlisted: int
    survivor_genome_ids: list[UUID]
    runtime_seconds: float
    futures_dimensions_tested: list[str]
```

### `SanadChainCompleted`

```python
class SanadChainCompletedPayload(BaseModel):
    sanad_card_id: UUID
    hypothesis_id: UUID
    policy_genome_id: UUID | None = None
    chain_results: list[dict]
    overall_verdict: Literal["PASS", "DISSENT", "FAIL"]
    confidence_tier: Literal["A", "B", "C"]
    confidence_numeric: float = Field(ge=0, le=1)
    dissent_summary: str | None = None
```

### `PoisoningSignalDetected`

```python
class PoisoningSignalDetectedPayload(BaseModel):
    detection_id: UUID
    signal_kind: Literal["citation_loop", "wording_similarity", "narrative_data_divergence", "source_concentration"]
    affected_claim: str | None = None
    affected_fact_ids: list[UUID]
    affected_source_ids: list[str]
    severity: Literal["info", "warning", "critical"]
    evidence: dict
    recommended_action: Literal["log", "quarantine_claim", "quarantine_source", "human_review"]
```

### `ApprovalRequested`

```python
class ApprovalRequestedPayload(BaseModel):
    approval_id: UUID
    requesting_workflow_id: UUID | None = None
    action_kind: str
    description: str
    payload_summary: str
    expires_at: datetime
    autonomy_level: Literal[5]
```

## Event registry

```python
EVENT_TYPE_REGISTRY: dict[str, type[BaseModel]] = {
    "SourceUpdateDetected": SourceUpdateDetectedPayload,
    "AccessGuardDecision": AccessGuardDecisionPayload,
    "RawArchiveAdded": RawArchiveAddedPayload,
    "FactExtracted": FactExtractedPayload,
    "InvestigationProposed": InvestigationProposedPayload,
    "PolicyGenomeProposed": PolicyGenomeProposedPayload,
    "ScenarioRunCompleted": ScenarioRunCompletedPayload,
    "SanadChainCompleted": SanadChainCompletedPayload,
    "PoisoningSignalDetected": PoisoningSignalDetectedPayload,
    "ApprovalRequested": ApprovalRequestedPayload,
}
```

## Event bus client

```python
class EventBus:
    async def emit(
        self,
        event_type: str,
        payload: BaseModel,
        producer_agent: str,
        correlation_id: UUID | None = None,
        causation_id: UUID | None = None,
    ) -> UUID: ...

    async def subscribe(
        self,
        stream: str,
        consumer_group: str,
        consumer_id: str,
    ) -> AsyncIterator[EventEnvelope]: ...

    async def ack(self, stream: str, consumer_group: str, redis_message_id: str) -> None: ...

    async def nack(self, stream: str, consumer_group: str, redis_message_id: str, reason: str) -> None: ...
```

## Idempotency

Every consumer must write an idempotency key in the same transaction as its side effect.

```sql
CREATE TABLE idempotency_keys (
    key TEXT PRIMARY KEY,
    consumer_id TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    result JSONB
);
```

## Audit integration

Redis Streams are operational. They are not the tamper-evident audit trail. The `audit_logger` consumer group consumes all streams and appends consequential events into the hash-chained Postgres audit log.

## Tests

`tests/events/test_bus.py` must include:

1. Emit → subscribe → ack.
2. Payload validation on emit.
3. Invalid payload rejected.
4. At-least-once replay on unacked event.
5. DLQ after 3 failures.
6. Idempotent consumer does not perform side effect twice.
7. Audit logger consumes and writes audit rows.
