# 04 — Memory Store Schemas

## Purpose

The five memory stores are the primary contracts for all agents. Agents may not improvise alternative shapes. All reads and writes must use these schemas or explicit database models generated from them.

## Store overview

| Store | Purpose | Can contain speculation? | Requires provenance? |
|---|---|---:|---:|
| Raw Archive | Immutable raw external material | No interpretation | Yes |
| Fact Store | Source-grounded extracted facts | No | Yes |
| Hypothesis Store | Unproven ideas and causal mechanisms | Yes, labeled as hypothesis | Yes for supporting evidence |
| Insight Corpus | Validated outputs | No unsupported speculation | Yes |
| Belief Calibration Store | Predictions and observed outcomes | Predictions only, tracked | Yes |

## Shared enums and helper models

```python
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, AnyUrl, confloat, conint

class TrustLabel(str, Enum):
    UNTRUSTED_EXTERNAL = "untrusted_external"
    SANITIZED_EXTERNAL = "sanitized_external"
    EXTRACTED_FACT = "extracted_fact"
    VALIDATED_FACT = "validated_fact"
    MODEL_GENERATED_HYPOTHESIS = "model_generated_hypothesis"
    HUMAN_REVIEWED = "human_reviewed"

class ValidationStatus(str, Enum):
    UNVALIDATED = "unvalidated"
    VALIDATION_PENDING = "validation_pending"
    VALIDATED = "validated"
    PARTIALLY_VALIDATED = "partially_validated"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    SUPERSEDED = "superseded"

class LifecycleStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    QUARANTINED = "quarantined"
    RETIRED = "retired"

class ExtractionMethod(str, Enum):
    DETERMINISTIC_API = "deterministic_api"
    DETERMINISTIC_PARSER = "deterministic_parser"
    GPT54_EXTRACTOR = "gpt54_extractor"
    OCR_PADDLE = "ocr_paddle"
    NOUGAT = "nougat"
    CAMELOT_TABLE = "camelot_table"
    HUMAN_REVIEW = "human_review"

class EvidenceSpan(BaseModel):
    span_id: UUID = Field(default_factory=uuid4)
    raw_id: UUID
    page_no: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    quote: Optional[str] = None
    table_ref: Optional[str] = None
    figure_ref: Optional[str] = None

class SourcePointer(BaseModel):
    source_id: UUID
    raw_id: Optional[UUID] = None
    url: Optional[AnyUrl] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    content_hash_sha256: Optional[str] = None

class ImpactEstimate(BaseModel):
    metric_name: str
    lower_bound: Optional[float] = None
    point_estimate: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: str
    currency: Optional[str] = None
    time_horizon: Optional[str] = None
    method: Optional[str] = None
    assumptions: list[str] = Field(default_factory=list)

class DisconfirmationTest(BaseModel):
    test_id: UUID = Field(default_factory=uuid4)
    statement: str
    metric: Optional[str] = None
    threshold: Optional[str] = None
    observation_window: Optional[str] = None
    data_source: Optional[str] = None
```

---

# Store 1 — Raw Archive

## Purpose

The Raw Archive is immutable. It stores external material exactly as retrieved, plus metadata. It does not store model interpretation.

## Lifecycle states

```text
INGESTED → SANITIZED → PARSED → EXTRACTED
       ↘ QUARANTINED
       ↘ SUPERSEDED
```

## Pydantic model

```python
class RawSourceType(str, Enum):
    API_JSON = "api_json"
    API_CSV = "api_csv"
    HTML_PAGE = "html_page"
    PDF = "pdf"
    DOCX = "docx"
    RSS_ITEM = "rss_item"
    IMAGE = "image"
    LAW_PAGE = "law_page"
    DATASET_EXPORT = "dataset_export"
    MANUAL_UPLOAD = "manual_upload"

class RetrievalMethod(str, Enum):
    API = "api"
    BULK_DOWNLOAD = "bulk_download"
    RSS = "rss"
    POLITE_HTTP = "polite_http"
    MANUAL_UPLOAD = "manual_upload"

class RawStatus(str, Enum):
    INGESTED = "ingested"
    SANITIZED = "sanitized"
    PARSED = "parsed"
    EXTRACTED = "extracted"
    QUARANTINED = "quarantined"
    SUPERSEDED = "superseded"

class RawArchiveRecord(BaseModel):
    raw_id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    access_decision_id: UUID
    source_type: RawSourceType
    retrieval_method: RetrievalMethod
    source_url: AnyUrl
    canonical_url: Optional[AnyUrl] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    retrieved_at: datetime
    content_type: str
    language_codes: list[str] = Field(default_factory=list)
    raw_storage_uri: str
    text_storage_uri: Optional[str] = None
    raw_text_preview: Optional[str] = Field(default=None, max_length=2000)
    content_hash_sha256: str
    normalized_content_hash_sha256: Optional[str] = None
    byte_size: int
    version_no: conint(ge=1) = 1
    previous_raw_id: Optional[UUID] = None
    supersedes_raw_id: Optional[UUID] = None
    superseded_by_raw_id: Optional[UUID] = None
    trust_label: TrustLabel = TrustLabel.UNTRUSTED_EXTERNAL
    status: RawStatus = RawStatus.INGESTED
    pii_risk_score: confloat(ge=0, le=1) = 0.0
    injection_risk_score: confloat(ge=0, le=1) = 0.0
    parse_error: Optional[str] = None
    retrieval_headers: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by_agent: str
    created_at: datetime
    updated_at: datetime
```

## Required indices and constraints

```sql
ALTER TABLE raw_archive ADD CONSTRAINT uq_raw_hash UNIQUE (content_hash_sha256);
CREATE INDEX idx_raw_source_time ON raw_archive(source_id, retrieved_at DESC);
CREATE INDEX idx_raw_status ON raw_archive(status);
CREATE INDEX idx_raw_type ON raw_archive(source_type);
CREATE INDEX idx_raw_supersession ON raw_archive(supersedes_raw_id, superseded_by_raw_id);
CREATE INDEX idx_raw_injection_risk ON raw_archive(injection_risk_score);
```

## Foreign keys

```text
raw_archive.source_id → source_registry.source_id
raw_archive.access_decision_id → access_decisions.decision_id
raw_archive.previous_raw_id → raw_archive.raw_id
raw_archive.supersedes_raw_id → raw_archive.raw_id
```

## Supersession rule

If the same canonical URL changes materially, insert a new Raw Archive record. Do not overwrite the old one. Set:

```text
new.previous_raw_id = old.raw_id
new.supersedes_raw_id = old.raw_id
old.superseded_by_raw_id = new.raw_id
old.status = SUPERSEDED
```

---

# Store 2 — Fact Store

## Purpose

The Fact Store contains only source-grounded extracted facts. A fact may be wrong, contradicted, or unvalidated, but it must not be model speculation.

## Pydantic model

```python
class FactType(str, Enum):
    INDICATOR_VALUE = "indicator_value"
    LEGAL_PROVISION = "legal_provision"
    TRADE_FLOW = "trade_flow"
    COMPANY_DISCLOSURE = "company_disclosure"
    FDI_PROJECT = "fdi_project"
    POLICY_ANNOUNCEMENT = "policy_announcement"
    REPORT_CLAIM = "report_claim"
    DATASET_METADATA = "dataset_metadata"
    CITATION_EDGE = "citation_edge"

class FactLifecycle(str, Enum):
    EXTRACTED = "extracted"
    VALIDATION_PENDING = "validation_pending"
    VALIDATED = "validated"
    CONTRADICTED = "contradicted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    QUARANTINED = "quarantined"

class FactStoreRecord(BaseModel):
    fact_id: UUID = Field(default_factory=uuid4)
    fact_type: FactType
    subject_key: str
    subject_label: Optional[str] = None
    predicate: str
    object_value: Any
    object_value_normalized: Optional[Any] = None
    unit: Optional[str] = None
    currency: Optional[str] = None
    country_code: Optional[str] = None
    sector_code: Optional[str] = None
    activity_code: Optional[str] = None
    indicator_code: Optional[str] = None
    time_period_start: Optional[date] = None
    time_period_end: Optional[date] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    source_raw_ids: list[UUID] = Field(default_factory=list)
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    extraction_method: ExtractionMethod
    extractor_name: str
    extractor_version: str
    extraction_prompt_hash: Optional[str] = None
    confidence_score: confloat(ge=0, le=1) = 0.50
    validation_status: ValidationStatus = ValidationStatus.UNVALIDATED
    lifecycle_status: FactLifecycle = FactLifecycle.EXTRACTED
    contradiction_group_id: Optional[UUID] = None
    supersedes_fact_id: Optional[UUID] = None
    superseded_by_fact_id: Optional[UUID] = None
    provenance_summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
```

## Required indices

```sql
CREATE INDEX idx_fact_type ON fact_store(fact_type);
CREATE INDEX idx_fact_subject ON fact_store(subject_key);
CREATE INDEX idx_fact_predicate ON fact_store(predicate);
CREATE INDEX idx_fact_country_sector ON fact_store(country_code, sector_code);
CREATE INDEX idx_fact_indicator_time ON fact_store(indicator_code, time_period_start, time_period_end);
CREATE INDEX idx_fact_validation ON fact_store(validation_status);
CREATE INDEX idx_fact_lifecycle ON fact_store(lifecycle_status);
CREATE INDEX idx_fact_confidence ON fact_store(confidence_score);
CREATE INDEX idx_fact_contradiction_group ON fact_store(contradiction_group_id);
CREATE INDEX idx_fact_object_json ON fact_store USING GIN (object_value_jsonb);
```

## Foreign keys

Use a join table for many-to-many raw evidence:

```sql
fact_sources(fact_id UUID REFERENCES fact_store, raw_id UUID REFERENCES raw_archive)
```

## Supersession rule

A corrected fact must not overwrite the old fact. Insert a new fact and set supersession fields. Contradictory facts may coexist if both are source-grounded; link them with `contradiction_group_id`.

---

# Store 3 — Hypothesis Store

## Purpose

The Hypothesis Store contains unproven ideas. It is allowed to contain speculation, but every hypothesis must be labeled as hypothesis and must point to supporting and contradicting evidence where available.

## Pydantic model

```python
class HypothesisType(str, Enum):
    POLICY_OPPORTUNITY = "policy_opportunity"
    FDI_GAP = "fdi_gap"
    IMPORT_SUBSTITUTION = "import_substitution"
    LEGAL_FRICTION = "legal_friction"
    PRODUCTIVITY_FRONTIER = "productivity_frontier"
    RISK_SIGNAL = "risk_signal"
    SCENARIO = "scenario"
    SOURCE_POISONING = "source_poisoning"

class HypothesisStatus(str, Enum):
    GENERATED = "generated"
    TRIAGED = "triaged"
    RESEARCH_QUEUED = "research_queued"
    SIMULATION_QUEUED = "simulation_queued"
    SIMULATED = "simulated"
    SANAD_PENDING = "sanad_pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PROMOTED_TO_INSIGHT = "promoted_to_insight"
    ARCHIVED = "archived"
    QUARANTINED = "quarantined"

class HypothesisStoreRecord(BaseModel):
    hypothesis_id: UUID = Field(default_factory=uuid4)
    hypothesis_type: HypothesisType
    title: str
    problem_statement: str
    proposed_mechanism: str
    target_outcomes: list[str] = Field(default_factory=list)
    anchor_fact_ids: list[UUID] = Field(default_factory=list)
    supporting_fact_ids: list[UUID] = Field(default_factory=list)
    contradicting_fact_ids: list[UUID] = Field(default_factory=list)
    related_raw_ids: list[UUID] = Field(default_factory=list)
    source_event_ids: list[UUID] = Field(default_factory=list)
    graph_node_ids: list[str] = Field(default_factory=list)
    generated_by_agent: str
    generation_method: str
    novelty_score: confloat(ge=0, le=10) = 0
    economic_relevance_score: confloat(ge=0, le=10) = 0
    evidence_strength_score: confloat(ge=0, le=10) = 0
    confidence_prior: confloat(ge=0, le=1) = 0.5
    uncertainty_drivers: list[str] = Field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.GENERATED
    next_action: Optional[str] = None
    owner_agent: Optional[str] = None
    rejection_reason: Optional[str] = None
    parent_hypothesis_id: Optional[UUID] = None
    supersedes_hypothesis_id: Optional[UUID] = None
    superseded_by_hypothesis_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Required indices

```sql
CREATE INDEX idx_hypothesis_type ON hypothesis_store(hypothesis_type);
CREATE INDEX idx_hypothesis_status ON hypothesis_store(status);
CREATE INDEX idx_hypothesis_scores ON hypothesis_store(economic_relevance_score DESC, novelty_score DESC);
CREATE INDEX idx_hypothesis_due ON hypothesis_store(due_at);
CREATE INDEX idx_hypothesis_parent ON hypothesis_store(parent_hypothesis_id);
```

## Promotion rule

A hypothesis may only be promoted to Insight Corpus after:

1. at least one supporting fact exists,
2. contradicting evidence has been checked,
3. Sanad validation status is not rejected,
4. a disconfirmation test is defined,
5. the promotion event is audit-logged.

---

# Store 4 — Insight Corpus

## Purpose

The Insight Corpus contains validated or review-ready outputs. It is the briefing-quality memory store.

## Pydantic model

```python
class InsightType(str, Enum):
    POLICY_OPPORTUNITY_CARD = "policy_opportunity_card"
    POLICY_GENOME_CARD = "policy_genome_card"
    FDI_GAP_CARD = "fdi_gap_card"
    LEGAL_FRICTION_CARD = "legal_friction_card"
    IMPORT_SUBSTITUTION_CARD = "import_substitution_card"
    RISK_CARD = "risk_card"
    WEEKLY_BRIEFING = "weekly_briefing"
    SCENARIO_RESULT = "scenario_result"

class ConfidenceTier(str, Enum):
    A = "A"  # strong multi-source evidence, validated, low unresolved contradiction
    B = "B"  # good evidence but assumptions remain
    C = "C"  # plausible, needs more evidence
    D = "D"  # weak or exploratory only

class InsightStatus(str, Enum):
    DRAFT = "draft"
    SANAD_VALIDATED = "sanad_validated"
    BRIEFING_READY = "briefing_ready"
    HUMAN_REVIEWED = "human_reviewed"
    ACTED_ON = "acted_on"
    SUPERSEDED = "superseded"
    RETIRED = "retired"
    QUARANTINED = "quarantined"

class RecommendedAction(BaseModel):
    action_id: UUID = Field(default_factory=uuid4)
    action_text: str
    owner_entity: Optional[str] = None
    time_horizon: Optional[str] = None
    required_decision: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)

class PilotDesign(BaseModel):
    pilot_name: str
    objective: str
    geography_or_scope: Optional[str] = None
    duration_days: Optional[int] = None
    success_metrics: list[str] = Field(default_factory=list)
    minimum_success_threshold: Optional[str] = None
    data_required: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)

class InsightCorpusRecord(BaseModel):
    insight_id: UUID = Field(default_factory=uuid4)
    insight_type: InsightType
    title: str
    executive_summary: str
    related_hypothesis_ids: list[UUID] = Field(default_factory=list)
    policy_genome_id: Optional[UUID] = None
    source_fact_ids: list[UUID] = Field(default_factory=list)
    source_raw_ids: list[UUID] = Field(default_factory=list)
    graph_node_ids: list[str] = Field(default_factory=list)
    estimated_impacts: list[ImpactEstimate] = Field(default_factory=list)
    confidence_tier: ConfidenceTier = ConfidenceTier.C
    confidence_score: confloat(ge=0, le=1) = 0.5
    sanad_validation_id: Optional[UUID] = None
    scenario_result_ids: list[UUID] = Field(default_factory=list)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    pilot_design: Optional[PilotDesign] = None
    disconfirmation_tests: list[DisconfirmationTest] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    status: InsightStatus = InsightStatus.DRAFT
    sensitivity_label: str = "internal"
    intended_audience: list[str] = Field(default_factory=list)
    supersedes_insight_id: Optional[UUID] = None
    superseded_by_insight_id: Optional[UUID] = None
    created_by_agent: str
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Required indices

```sql
CREATE INDEX idx_insight_type ON insight_corpus(insight_type);
CREATE INDEX idx_insight_status ON insight_corpus(status);
CREATE INDEX idx_insight_confidence ON insight_corpus(confidence_tier, confidence_score DESC);
CREATE INDEX idx_insight_created ON insight_corpus(created_at DESC);
CREATE INDEX idx_insight_policy_genome ON insight_corpus(policy_genome_id);
```

---

# Store 5 — Belief Calibration Store

## Purpose

The Belief Calibration Store tracks whether the system becomes more accurate over time. It turns confidence from decoration into measured reliability.

## Pydantic model

```python
class BeliefStatus(str, Enum):
    PENDING = "pending"
    OUTCOME_OBSERVED = "outcome_observed"
    CALIBRATED = "calibrated"
    OVERDUE = "overdue"
    VOIDED = "voided"

class ErrorCategory(str, Enum):
    CORRECT = "correct"
    WRONG_DIRECTION = "wrong_direction"
    WRONG_MAGNITUDE = "wrong_magnitude"
    WRONG_TIMING = "wrong_timing"
    BAD_SOURCE = "bad_source"
    BAD_CAUSAL_ASSUMPTION = "bad_causal_assumption"
    IMPLEMENTATION_ASSUMPTION_FAILED = "implementation_assumption_failed"
    EXTERNAL_SHOCK = "external_shock"
    INSUFFICIENT_DATA = "insufficient_data"

class OutcomeObservation(BaseModel):
    observed_value: Optional[float] = None
    observed_category: Optional[str] = None
    unit: Optional[str] = None
    observation_date: date
    observation_source_fact_ids: list[UUID] = Field(default_factory=list)
    observation_notes: Optional[str] = None

class BeliefCalibrationRecord(BaseModel):
    belief_id: UUID = Field(default_factory=uuid4)
    linked_hypothesis_id: Optional[UUID] = None
    linked_insight_id: Optional[UUID] = None
    linked_prediction_event_id: Optional[UUID] = None
    claim: str
    expected_outcome_metric: str
    expected_lower_bound: Optional[float] = None
    expected_point_estimate: Optional[float] = None
    expected_upper_bound: Optional[float] = None
    expected_unit: str
    confidence_score: confloat(ge=0, le=1)
    time_horizon_start: date
    time_horizon_end: date
    due_date: date
    status: BeliefStatus = BeliefStatus.PENDING
    evidence_fact_ids: list[UUID] = Field(default_factory=list)
    source_reliability_snapshot: dict[str, float] = Field(default_factory=dict)
    model_or_agent_snapshot: dict[str, Any] = Field(default_factory=dict)
    outcome: Optional[OutcomeObservation] = None
    calibration_error: Optional[float] = None
    brier_score: Optional[float] = None
    log_score: Optional[float] = None
    direction_correct: Optional[bool] = None
    magnitude_error_pct: Optional[float] = None
    error_category: Optional[ErrorCategory] = None
    lesson_learned: Optional[str] = None
    model_update_recommended: bool = False
    source_reliability_adjustments: dict[str, float] = Field(default_factory=dict)
    agent_weight_adjustments: dict[str, float] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    calibrated_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Required indices

```sql
CREATE INDEX idx_belief_status_due ON belief_calibration(status, due_date);
CREATE INDEX idx_belief_insight ON belief_calibration(linked_insight_id);
CREATE INDEX idx_belief_hypothesis ON belief_calibration(linked_hypothesis_id);
CREATE INDEX idx_belief_confidence ON belief_calibration(confidence_score);
CREATE INDEX idx_belief_error_category ON belief_calibration(error_category);
```

## Calibration rules

1. Every insight with a time-bound expected outcome must create a belief record.
2. Confidence scores must be evaluated when outcome data becomes available.
3. Overdue beliefs are flagged in Fath Canvas.
4. Source reliability and agent weights may be adjusted only through calibration events, not ad hoc.
5. A human reviewer may void a belief only with a reason.

---

# Store separation rules

1. Raw Archive never stores interpretations.
2. Fact Store never stores hypotheses.
3. Hypothesis Store never becomes evidence by itself.
4. Insight Corpus requires validation.
5. Belief Calibration Store evaluates claims over time.
6. Every promotion between stores emits an audit event.
7. Every object has provenance.
8. Every supersession preserves the old record.
