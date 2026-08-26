# 08 — Agent Role Specifications

## Design rule

Use a small number of role definitions with many task instances. Do not create thousands of unique agents.

## Role groups

### Research and ingestion agents

| Agent | Responsibility | Writes to |
|---|---|---|
| Source Scout | Maintains source registry, detects source-level changes. | Source Registry, Event Log |
| Access Guard | Approves/rejects source access. | Access Decisions, Event Log |
| API Crawler | Fetches approved API/export sources. | Raw Archive |
| Legal Crawler | Conservatively collects public legal corpus. | Raw Archive |
| Report Crawler | Collects public PDFs/reports. | Raw Archive |
| News/Event Crawler | Fetches GDELT/RSS/event signals. | Raw Archive |
| Benchmark Crawler | Tracks peer-country policy/economic sources. | Raw Archive |
| Parser | Converts raw material into normalized text/tables. | Raw Archive metadata |
| Document Sanitizer | Wraps all external content as UntrustedBlob. | Event Log, Raw metadata |

### Knowledge agents

| Agent | Responsibility | Writes to |
|---|---|---|
| Extractor | Extracts structured facts from sanitized content. | Fact Store |
| Entity Resolver | Deduplicates entities and identifiers. | Fact Store, Graph |
| Knowledge Graph Builder | Creates graph nodes/edges with provenance. | Apache AGE graph, Event Log |
| Change Detector | Compares versions and detects deltas. | Event Log, Hypothesis Store |
| Anomaly Miner | Detects unusual values, movements, or gaps. | Event Log, Hypothesis Store |
| Connection Agent | Finds cross-domain links. | Event Log, Hypothesis Store |

### Reasoning agents

| Agent | Responsibility | Writes to |
|---|---|---|
| Coverage Auditor | Finds blind spots and uncomfortable investigations. | Hypothesis Store, Event Log |
| Hypothesis Generator | Generates policy/economic hypotheses. | Hypothesis Store |
| Policy Genome Generator | Converts hypotheses into structured policy packages. | Hypothesis Store, Insight drafts |
| Scenario Runner | Stress-tests policy genomes. | Simulation results, Event Log |
| Causal Skeptic | Attacks causal claims. | Sanad inputs, Hypothesis status |
| Sanad Validator | Validates evidence, numbers, causality, dissent, feasibility. | Insight Corpus |

### Trust and evolution agents

| Agent | Responsibility | Writes to |
|---|---|---|
| Source-Poisoning Detector | Detects narrative manipulation and source poisoning. | Hypothesis Store, Event Log |
| Belief Calibration Agent | Tracks predictions against outcomes. | Belief Calibration Store |
| Audit Logger | Writes tamper-evident audit rows. | Audit Log |

### UI agents

| Agent | Responsibility | Writes to |
|---|---|---|
| UI Orchestrator | Converts events into approved UI specs. | Event Log / UI API |
| Briefing Composer | Produces weekly briefings. | Insight Corpus |
| Run Replay Builder | Reconstructs source-to-insight paths. | UI API |
| Approval Marshal | Manages human approval gates. | Approval tables, Event Log |

## Agent input/output contract

Every agent receives:

```python
class AgentInputEnvelope(BaseModel):
    run_id: UUID
    task_id: UUID
    agent_name: str
    budget_key: str
    input_object_ids: list[UUID]
    input_event_ids: list[UUID]
    instructions: dict[str, Any]
    created_at: datetime
```

Every agent returns:

```python
class AgentOutputEnvelope(BaseModel):
    run_id: UUID
    task_id: UUID
    agent_name: str
    success: bool
    output_object_ids: list[UUID]
    emitted_event_ids: list[UUID]
    error_message: Optional[str] = None
    retry_recommended: bool = False
    completed_at: datetime
```

## Agent boundary rules

1. Crawlers cannot call GPT-5.4.
2. Extractors cannot write hypotheses.
3. Hypothesis agents cannot write Fact Store records.
4. UI Orchestrator cannot change analysis results.
5. Approval Marshal cannot approve its own requests.
6. Source-Poisoning Detector can quarantine a claim cluster, not delete facts.
7. Belief Calibration Agent can adjust reliability scores only through logged calibration events.

## Coverage Auditor prominence

The Coverage Auditor is not a minor agent. It is a strategic subsystem.

It runs Al-Muhāsibī discipline and asks:

```text
What are we not looking at?
Which sources are overrepresented?
Which sectors look boring but may hide leverage?
Which obvious consulting recommendations should be rejected?
Which competitor-country move did Qatar not respond to?
Which public signal contradicts the current strategy narrative?
```

The weekly briefing must lead with its top autonomous investigations.
