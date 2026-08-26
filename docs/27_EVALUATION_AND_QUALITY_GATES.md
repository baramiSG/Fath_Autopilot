# 27 — Evaluation, Golden Sets, and Quality Gates

## Purpose

Fath must not become an impressive-looking system with unknown accuracy. This document defines the evaluation harness, golden datasets, quality gates, and regression workflow required before each build phase is accepted.

## Evaluation principle

Every autonomous capability must have a measurable contract.

```text
Crawler      → did it fetch the right public resource safely?
Extractor    → did it extract the right facts with correct provenance?
Retriever    → did it retrieve the evidence needed for the question?
Graph        → did it create correct nodes and edges?
Connection   → did it find useful non-obvious links without hallucination?
Sanad        → did it accept strong claims and reject weak claims?
Canvas       → did it render validated specs without freeform JSON drift?
Calibration  → did confidence become better over time?
```

## Golden dataset structure

Create a `golden/` folder in the repository:

```text
golden/
├── sources/
│   ├── qatar_open_data_sample.json
│   ├── world_bank_qatar_indicators.json
│   ├── gdelt_sample.json
│   ├── al_meezan_sample_html_ar.html
│   └── al_meezan_sample_html_en.html
├── extractions/
│   ├── economic_indicator_expected.json
│   ├── legal_constraint_expected.json
│   ├── trade_flow_expected.json
│   └── policy_claim_expected.json
├── graph/
│   ├── expected_nodes.json
│   └── expected_edges.json
├── retrieval/
│   ├── queries.json
│   └── expected_evidence_spans.json
├── sanad/
│   ├── strong_hypotheses.json
│   ├── weak_hypotheses.json
│   ├── numerically_bad_hypotheses.json
│   └── infeasible_hypotheses.json
└── canvas/
    ├── event_payloads.json
    └── expected_component_specs.json
```

## Golden item schema

```python
class GoldenCase(BaseModel):
    case_id: str
    title: str
    input_refs: list[str]
    expected_output_ref: str
    metric: str
    minimum_score: float
    notes: str = ""
```

## Evaluation command

```bash
make eval
```

Runs:

```text
pytest unit tests
golden extraction eval
golden retrieval eval
golden graph eval
golden Sanad eval
Canvas schema roundtrip eval
security regression tests
```

## Extraction quality gates

| Extractor | Metric | Minimum |
|---|---:|---:|
| Economic indicator | exact field match F1 | 0.95 |
| Trade flow | HS code + value + year exact match | 0.95 |
| Legal constraint | affected article + constraint type F1 | 0.85 |
| Company disclosure | table value extraction F1 | 0.90 |
| Policy claim | claim classification F1 | 0.85 |

A fact extraction is wrong if any of these fail:

```text
wrong value
wrong unit
wrong year/period
wrong source reference
wrong law/article
unsupported claim
missing provenance
```

## Retrieval quality gates

Use retrieval queries with known evidence spans.

```python
class RetrievalEvalCase(BaseModel):
    query: str
    expected_fact_ids: list[UUID]
    expected_raw_archive_ids: list[UUID]
    expected_quote_hashes: list[str]
```

Metrics:

```text
Recall@20 >= 0.90
Recall@6  >= 0.75 after reranking
MRR       >= 0.65
Unsupported evidence rate <= 0.05
```

## Graph quality gates

Graph Builder is tested against expected nodes/edges.

```text
Node precision >= 0.95
Node recall    >= 0.90
Edge precision >= 0.90
Edge recall    >= 0.85
No edge without source_refs
No orphan source_refs
No duplicate canonical nodes above similarity threshold
```

## Connection Agent quality gates

The Connection Agent is judged by usefulness and grounding.

Golden cases include known cross-domain links such as:

```text
legal article → business activity → sector → trade product → import growth
regional benchmark policy → FDI project gap → Qatar target sector
QSE disclosure risk → sector productivity indicator → policy lever
```

Metrics:

```text
Grounded connection rate >= 0.90
Novel useful connection rate >= 0.40
Hallucinated connection rate <= 0.05
Duplicate connection rate <= 0.15
```

A connection is hallucinated if the graph path does not exist or if the narrative summary adds unsupported causal claims.

## Sanad quality gates

Sanad must correctly classify curated cases.

| Case type | Expected outcome |
|---|---|
| Strong, well-supported hypothesis | PASS / Tier A |
| Insufficient evidence | DISSENT or FAIL |
| Numerical mismatch | FAIL |
| No historical analog | DISSENT |
| Strong red-team flaw | FAIL |
| Execution infeasible | FAIL |

Minimum:

```text
Strong-pass accuracy >= 0.85
Weak-reject accuracy >= 0.90
Numerical failure detection = 1.00
No Tier-A publication without EvidenceBundle
```

## Fath Canvas quality gates

```text
All backend ComponentSpecs validate by Pydantic.
All frontend specs validate by Zod.
Unknown component renders fallback.
Invalid payload never renders normal component.
No component executes payload-supplied code.
SSE stream filters by RBAC role.
```

## Source-poisoning quality gates

Synthetic attack fixtures must trigger:

```text
citation loop detection
wording similarity cluster
narrative-vs-data divergence
source concentration
quarantine cascade
```

False-positive baseline:

```text
Mixed legitimate reporting over 30 days must not produce critical signal.
```

## Security quality gates

Must pass before any autonomous crawler runs continuously:

```text
Trust boundary delimiter spoofing test
Prompt-injection detection test
No raw web text as system/user instructions except UntrustedBlob-delimited data section
No unrestricted shell in agent modules
No network in simulation sandbox
No external action endpoints active without RBAC + approval
Audit chain verification passes
```

## Weekly regression workflow

```text
Every Sunday before weekly tournament:
1. Run unit tests.
2. Run golden evals.
3. Run trust-boundary tests.
4. Verify audit chain recent 10,000 rows.
5. Verify source registry active sources.
6. Generate evaluation report.
7. If any critical gate fails, weekly tournament is skipped and an alert appears in Canvas.
```

## Evaluation report schema

```python
class EvalMetric(BaseModel):
    name: str
    value: float
    threshold: float
    passed: bool
    details: dict = Field(default_factory=dict)

class EvalReport(BaseModel):
    report_id: UUID
    generated_at: datetime
    git_commit: str
    metrics: list[EvalMetric]
    overall_passed: bool
    critical_failures: list[str] = Field(default_factory=list)
```

```sql
CREATE TABLE eval_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    git_commit TEXT NOT NULL,
    metrics JSONB NOT NULL,
    overall_passed BOOLEAN NOT NULL,
    critical_failures TEXT[] NOT NULL DEFAULT '{}'
);
```

## Phase gates

### Week 1 gate

```text
Source registry loads
Access Guard decisions correct
Crawlers archive raw records idempotently
Trust boundary tests pass
Canvas renders Week 1 cards
Audit chain verifies
```

### Week 2 gate

```text
Extractors meet golden thresholds
Fact Store lifecycle works
Knowledge graph inserts nodes/edges with provenance
EvidenceGraphExplorer renders graph subset
```

### Week 3 gate

```text
Connection Agent generates grounded connections
Coverage Auditor proposes investigations
Hypothesis Store separates speculation from facts
Al-Muhāsibī novelty threshold enforced
```

### Week 4 gate

```text
Policy genomes generated in schema
Simulation tournament runs in sandbox
ScenarioTournamentView renders
Dominated genomes eliminated correctly
```

### Week 5 gate

```text
Sanad five chains pass fixtures
Source-poisoning detectors fire on synthetic attacks
Belief Calibration Store records predictions
Approval policies enforced
```

### Week 6 gate

```text
Autonomous weekly briefing generated
At least five unprompted investigations shown
At least one validated policy genome reaches Tier A or Tier B
RunReplay can reconstruct the evidence chain
Pitch demo runs end-to-end
```

## Non-negotiable rule

A feature is not complete because it works once. It is complete when it has:

```text
schema
storage
events
tests
evaluation case
audit trail
Canvas visibility
failure behavior
```
