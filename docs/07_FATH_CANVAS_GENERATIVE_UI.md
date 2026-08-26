# 07 — Fath Canvas Generative UI Contracts

## Purpose

Fath Canvas is the command surface of the autonomous system. It must show what Fath discovered, what it wants to investigate, what it rejected, and what requires human approval.

Fath Canvas is **controlled generative UI**. The model may output JSON UI specs that reference approved components. The model may not generate executable frontend code.

## First screen rule

The first screen must lead with:

> **What Fath wants to investigate next**

This demonstrates agency. Do not bury it below charts.

## Backend component contract

```python
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, confloat

class ComponentType(str, Enum):
    AUTOPILOT_PULSE = "AutopilotPulse"
    INVESTIGATION_QUEUE = "InvestigationQueue"
    INVESTIGATION_CARD = "InvestigationCard"
    SOURCE_UPDATE_CARD = "SourceUpdateCard"
    ACCESS_GUARD_DECISION_CARD = "AccessGuardDecisionCard"
    RAW_ARCHIVE_RECORD_CARD = "RawArchiveRecordCard"
    EARLY_FACT_CARD = "EarlyFactCard"
    APPROVAL_GATE_CARD = "ApprovalGateCard"
    EVIDENCE_GRAPH_EXPLORER = "EvidenceGraphExplorer"
    POLICY_GENOME_CARD = "PolicyGenomeCard"
    SANAD_VALIDATION_CARD = "SanadValidationCard"
    SCENARIO_TOURNAMENT_VIEW = "ScenarioTournamentView"
    SOURCE_INTEGRITY_RADAR = "SourceIntegrityRadar"
    BELIEF_CALIBRATION_PANEL = "BeliefCalibrationPanel"
    RUN_REPLAY = "RunReplay"
    WEEKLY_BRIEFING = "WeeklyBriefing"

class UISpecBase(BaseModel):
    spec_id: UUID = Field(default_factory=uuid4)
    component_type: ComponentType
    event_ids: list[UUID] = Field(default_factory=list)
    layout_priority: int = 100
    generated_at: datetime
    generated_by_agent: str = "ui_orchestrator"
```

## Component prop models

### AutopilotPulse

```python
class PulseMetric(BaseModel):
    label: str
    value: int | float | str
    delta: Optional[str] = None
    severity: Literal["neutral", "positive", "warning", "critical"] = "neutral"

class AutopilotPulseProps(BaseModel):
    period_label: str
    sources_checked: int
    raw_records_archived: int
    facts_extracted: int
    graph_edges_created: int
    hypotheses_generated: int
    simulations_run: int = 0
    insights_validated: int = 0
    items_rejected: int = 0
    metrics: list[PulseMetric] = Field(default_factory=list)
```

### InvestigationQueue and InvestigationCard

```python
class InvestigationItem(BaseModel):
    investigation_id: UUID
    title: str
    question: str
    why_now: str
    expected_economic_relevance: confloat(ge=0, le=1)
    novelty_score: confloat(ge=0, le=10)
    evidence_available_score: confloat(ge=0, le=1)
    source_count: int
    recommended_next_action: str
    approval_required: bool = False
    status: Literal["proposed", "approved", "rejected", "running", "completed"] = "proposed"

class InvestigationQueueProps(BaseModel):
    headline: str = "What Fath wants to investigate next"
    items: list[InvestigationItem]

class InvestigationCardProps(InvestigationItem):
    supporting_fact_ids: list[UUID] = Field(default_factory=list)
    graph_node_ids: list[str] = Field(default_factory=list)
```

### SourceUpdateCard

```python
class SourceUpdateCardProps(BaseModel):
    source_id: UUID
    source_name: str
    source_class: str
    checked_url: str
    changed_since_last_check: bool
    change_summary: Optional[str] = None
    last_checked_at: datetime
    next_check_at: Optional[datetime] = None
```

### AccessGuardDecisionCard

```python
class AccessGuardDecisionCardProps(BaseModel):
    decision_id: UUID
    source_name: str
    url: str
    decision_status: str
    reason: str
    rate_limit_per_minute: int
    max_pages: int
    requires_human_review: bool
```

### RawArchiveRecordCard

```python
class RawArchiveRecordCardProps(BaseModel):
    raw_id: UUID
    source_name: str
    title: Optional[str] = None
    source_url: str
    content_type: str
    byte_size: int
    content_hash_sha256: str
    retrieved_at: datetime
    status: str
```

### EarlyFactCard

```python
class EarlyFactCardProps(BaseModel):
    fact_id: UUID
    fact_type: str
    subject_label: str
    predicate: str
    object_value_display: str
    confidence_score: confloat(ge=0, le=1)
    source_count: int
    validation_status: str
```

### ApprovalGateCard

```python
class ApprovalOption(BaseModel):
    option_id: str
    label: str
    consequence: str

class ApprovalGateCardProps(BaseModel):
    approval_id: UUID
    requested_action: str
    target_object_type: str
    target_object_id: UUID
    risk_reason: str
    options: list[ApprovalOption]
    expires_at: Optional[datetime] = None
```

### EvidenceGraphExplorer

```python
class EvidenceGraphNode(BaseModel):
    node_id: str
    label: str
    node_type: str
    confidence_score: confloat(ge=0, le=1) = 0.5

class EvidenceGraphEdge(BaseModel):
    edge_id: str
    from_node_id: str
    to_node_id: str
    edge_type: str
    evidence_fact_ids: list[UUID]
    confidence_score: confloat(ge=0, le=1) = 0.5

class EvidenceGraphExplorerProps(BaseModel):
    title: str
    nodes: list[EvidenceGraphNode]
    edges: list[EvidenceGraphEdge]
    focus_node_id: Optional[str] = None
```

### PolicyGenomeCard

```python
class PolicyLeverView(BaseModel):
    lever_type: str
    lever_description: str
    owner_entity: Optional[str] = None
    expected_effect: Optional[str] = None

class PolicyGenomeCardProps(BaseModel):
    policy_genome_id: UUID
    title: str
    target_sector: str
    target_metric: str
    economic_problem: str
    proposed_mechanism: str
    levers: list[PolicyLeverView]
    estimated_impact: str
    confidence_tier: str
    pilot_design_summary: Optional[str] = None
    disconfirmation_test_summary: Optional[str] = None
```

### SanadValidationCard

```python
class SanadChainScoreView(BaseModel):
    chain_name: str
    score: confloat(ge=0, le=1)
    verdict: Literal["pass", "partial", "fail"]
    summary: str

class SanadValidationCardProps(BaseModel):
    sanad_validation_id: UUID
    target_title: str
    overall_confidence_tier: str
    chain_scores: list[SanadChainScoreView]
    dissent_recorded: bool
    recommendation: str
```

### ScenarioTournamentView

```python
class TournamentCandidateView(BaseModel):
    candidate_id: UUID
    title: str
    rank: int
    robustness_score: confloat(ge=0, le=1)
    expected_impact_score: confloat(ge=0, le=1)
    feasibility_score: confloat(ge=0, le=1)

class ScenarioTournamentViewProps(BaseModel):
    tournament_id: UUID
    generated_count: int
    rejected_count: int
    simulated_count: int
    survived_count: int
    shortlisted_count: int
    top_candidates: list[TournamentCandidateView]
```

### SourceIntegrityRadar

```python
class SourceIntegrityItem(BaseModel):
    source_id: UUID
    source_name: str
    reliability_score: confloat(ge=0, le=1)
    independence_score: confloat(ge=0, le=1)
    poisoning_risk_score: confloat(ge=0, le=1)
    notes: Optional[str] = None

class SourceIntegrityRadarProps(BaseModel):
    claim_cluster_id: Optional[UUID] = None
    title: str
    items: list[SourceIntegrityItem]
    recommended_action: str
```

### BeliefCalibrationPanel

```python
class CalibrationMetricView(BaseModel):
    label: str
    value: str
    explanation: Optional[str] = None

class BeliefCalibrationPanelProps(BaseModel):
    period_label: str
    total_beliefs_due: int
    calibrated_count: int
    overdue_count: int
    average_calibration_error: Optional[float] = None
    metrics: list[CalibrationMetricView] = Field(default_factory=list)
```

### RunReplay

```python
class RunReplayStep(BaseModel):
    sequence_no: int
    occurred_at: datetime
    agent_name: str
    event_type: str
    title: str
    summary: str
    event_id: UUID

class RunReplayProps(BaseModel):
    run_id: UUID
    title: str
    steps: list[RunReplayStep]
```

### Discriminated UI spec union

```python
class ComponentSpec(BaseModel):
    spec_id: UUID = Field(default_factory=uuid4)
    component_type: ComponentType
    layout_priority: int = 100
    event_ids: list[UUID] = Field(default_factory=list)
    props: dict
    generated_at: datetime

# Runtime validation rule:
# component_type determines which Props model validates props.
```

## TypeScript interfaces

```typescript
export type ComponentType =
  | "AutopilotPulse"
  | "InvestigationQueue"
  | "InvestigationCard"
  | "SourceUpdateCard"
  | "AccessGuardDecisionCard"
  | "RawArchiveRecordCard"
  | "EarlyFactCard"
  | "ApprovalGateCard"
  | "EvidenceGraphExplorer"
  | "PolicyGenomeCard"
  | "SanadValidationCard"
  | "ScenarioTournamentView"
  | "SourceIntegrityRadar"
  | "BeliefCalibrationPanel"
  | "RunReplay"
  | "WeeklyBriefing";

export interface ComponentSpec<TProps = unknown> {
  spec_id: string;
  component_type: ComponentType;
  layout_priority: number;
  event_ids: string[];
  props: TProps;
  generated_at: string;
}

export interface InvestigationItem {
  investigation_id: string;
  title: string;
  question: string;
  why_now: string;
  expected_economic_relevance: number;
  novelty_score: number;
  evidence_available_score: number;
  source_count: number;
  recommended_next_action: string;
  approval_required: boolean;
  status: "proposed" | "approved" | "rejected" | "running" | "completed";
}

export interface InvestigationQueueProps {
  headline: string;
  items: InvestigationItem[];
}

export interface AutopilotPulseProps {
  period_label: string;
  sources_checked: number;
  raw_records_archived: number;
  facts_extracted: number;
  graph_edges_created: number;
  hypotheses_generated: number;
  simulations_run: number;
  insights_validated: number;
  items_rejected: number;
  metrics: Array<{ label: string; value: number | string; delta?: string; severity: string }>;
}

export interface SourceUpdateCardProps {
  source_id: string;
  source_name: string;
  source_class: string;
  checked_url: string;
  changed_since_last_check: boolean;
  change_summary?: string;
  last_checked_at: string;
  next_check_at?: string;
}

export interface ApprovalGateCardProps {
  approval_id: string;
  requested_action: string;
  target_object_type: string;
  target_object_id: string;
  risk_reason: string;
  options: Array<{ option_id: string; label: string; consequence: string }>;
  expires_at?: string;
}
```

## UI Orchestrator rules

1. Only emit approved `component_type` values.
2. Validate every `props` object against the backend Pydantic model before returning it.
3. The frontend validates again with TypeScript/Zod or generated JSON Schema.
4. Reject unknown fields unless explicitly allowed.
5. Never render raw HTML from model output.
6. Never execute model-generated code.
7. Every UI component must link back to `event_ids`.
8. Every event-backed component should support run replay.

## First v0 screen layout

```text
Top:
- InvestigationQueue: What Fath wants to investigate next

Second:
- AutopilotPulse

Third:
- SourceUpdateCard stream
- AccessGuardDecisionCard stream
- EarlyFactCard stream

Fourth:
- ApprovalGateCard, only if pending approvals exist
```

## Rejection behavior

If GPT-5.4 returns an invalid UI spec:

1. validate and reject,
2. emit `ui_spec_rendered` event with error status,
3. ask the UI Orchestrator to retry once with the validation error,
4. if invalid again, render a safe fallback event card.
