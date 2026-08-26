# 13 — Workflows, Heartbeats, and State

## Purpose

The system is proactive through scheduled heartbeat workflows. Prefect triggers workflows. LangGraph executes stateful agent graphs.

## Implementation decision

- Prefect 3 schedules and monitors flows.
- LangGraph defines workflow state transitions.
- Postgres stores workflow state snapshots.
- Every step is idempotent.
- Partial failure resumes from the last successful state.

## Heartbeat schedules

| Cadence | Workflow | Purpose |
|---|---|---|
| Hourly | `source_check_heartbeat` | Check approved source changes. |
| Daily | `ingestion_and_fact_heartbeat` | Archive, sanitize, parse, extract facts. |
| Daily | `graph_and_anomaly_heartbeat` | Update graph, detect anomalies. |
| Twice weekly | `coverage_audit_heartbeat` | Find blind spots and propose investigations. |
| Weekly | `policy_tournament_heartbeat` | Generate and test policy genomes. |
| Weekly | `briefing_heartbeat` | Produce autonomous weekly briefing. |
| Monthly | `calibration_and_integrity_heartbeat` | Calibrate beliefs and review source integrity. |

## Workflow state schema

```python
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED_FOR_APPROVAL = "paused_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStateRecord(BaseModel):
    run_id: UUID
    workflow_name: str
    status: WorkflowStatus
    current_node: Optional[str]
    completed_nodes: list[str] = Field(default_factory=list)
    failed_nodes: list[str] = Field(default_factory=list)
    state_payload: dict[str, Any]
    budget_key: str
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    parent_run_id: Optional[UUID] = None
```

## LangGraph node pattern

Every node must:

1. read state,
2. check budget,
3. check idempotency key,
4. perform bounded work,
5. write outputs,
6. emit events,
7. update workflow state,
8. return next node.

## Idempotency key format

```text
{workflow_name}:{run_id}:{node_name}:{input_hash}
```

## Source check heartbeat graph

```text
START
  ↓
load_enabled_sources
  ↓
for_each_source: access_guard_review
  ↓
source_scout_check_hash_or_metadata
  ↓
emit_source_checked_events
  ↓
queue_ingestion_for_changed_sources
  ↓
END
```

## Daily ingestion graph

```text
START
  ↓
load_changed_sources
  ↓
fetch_with_crawler
  ↓
archive_raw
  ↓
sanitize_untrusted_content
  ↓
parse_content
  ↓
extract_facts
  ↓
validate_basic_facts
  ↓
emit_events
  ↓
END
```

## Graph/anomaly graph

```text
START
  ↓
load_new_validated_facts
  ↓
resolve_entities
  ↓
update_graph_nodes_edges
  ↓
run_change_detector
  ↓
run_anomaly_miner
  ↓
run_connection_agent
  ↓
propose_investigations
  ↓
END
```

## Coverage audit graph

```text
START
  ↓
load_recent_graph_summary
  ↓
load_recent_insight_corpus
  ↓
load_rejected_hypotheses
  ↓
run_al_muhasibi_coverage_auditor
  ↓
create_investigation_hypotheses
  ↓
rank_investigations
  ↓
emit_investigation_queue_events
  ↓
END
```

## Policy tournament graph

```text
START
  ↓
load_approved_or_high_score_hypotheses
  ↓
generate_policy_genomes
  ↓
run_pre_validation_filters
  ↓
run_scenario_stress_tests
  ↓
run_causal_skeptic
  ↓
run_sanad_validation
  ↓
promote_survivors_to_insight_corpus
  ↓
create_belief_calibration_records
  ↓
END
```

## Partial failure semantics

If a node fails:

1. write failure event,
2. store node failure in workflow state,
3. retry according to node policy,
4. if retry exhausted, move event to dead letter,
5. if downstream nodes can proceed safely, continue degraded,
6. otherwise pause workflow and require review.

## Resume semantics

On resume:

1. load latest `WorkflowStateRecord`,
2. skip completed nodes with matching idempotency keys,
3. rerun failed or pending nodes,
4. preserve prior emitted events,
5. never delete prior outputs.

## Human-in-the-loop pause

If a workflow reaches an approval node:

```text
status = PAUSED_FOR_APPROVAL
emit approval_required event
wait for approval_marshal decision
resume from approval node after decision
```
