# 14 — Budget, Rate Limits, and Circuit Breakers

## Purpose

Every autonomous loop must be bounded. This prevents runaway crawling, runaway API usage, runaway model calls, and denial-of-wallet behavior.

## Implementation decision

Use Redis for runtime counters and circuit breakers. Postgres remains the source of truth for durable records.

## Budget scopes

| Scope | Example |
|---|---|
| per_cycle | one hourly heartbeat run |
| per_workflow | one LangGraph workflow run |
| per_source | one source per cycle |
| per_agent | one agent role per workflow |
| per_model | GPT-5.4 token budget |
| per_user_action | human-triggered investigation |

## Redis key format

```text
budget:{scope}:{scope_id}:{limit_name}
```

Examples:

```text
budget:cycle:2026-05-08T12:00Z:max_sources_checked
budget:source:almeezan:max_pages
budget:model:gpt54:tokens_in
budget:model:gpt54:tokens_out
budget:workflow:run_uuid:max_runtime_seconds
```

## Budget model

```python
class BudgetLimit(BaseModel):
    budget_key: str
    scope: str
    limit_name: str
    limit_value: float
    current_value: float = 0
    reset_at: datetime
    warning_threshold_pct: float = 0.80
    hard_limit: bool = True

class BudgetDecision(BaseModel):
    allowed: bool
    budget_key: str
    limit_name: str
    remaining: float
    action_on_breach: str
    message: str
```

## Atomic decrement

All budget checks must use atomic Redis operations.

Pseudocode:

```text
1. Read current counter.
2. If increment would exceed limit, return not allowed.
3. Else increment counter atomically.
4. Set TTL if first use.
5. Emit warning if above threshold.
```

## Circuit breaker behavior

| Breach type | Behavior |
|---|---|
| Per-source page limit | Stop source; queue remaining URLs for next cycle. |
| Per-cycle source limit | End cycle gracefully. |
| Model token warning | Switch to shorter prompts or defer low-priority tasks. |
| Model token hard breach | Stop model calls and emit alert. |
| Runtime breach | Save state and resume next cycle. |
| Error-rate breach | Disable source temporarily and require review. |
| Injection-risk breach | Quarantine source output. |

## Initial budget defaults

```yaml
hourly_source_check:
  max_sources_checked: 50
  max_runtime_seconds: 900
  max_llm_calls: 0

daily_ingestion:
  max_sources: 20
  max_pages_per_source: 200
  max_bytes_per_source: 500000000
  max_runtime_seconds: 7200
  max_llm_calls: 200

coverage_audit:
  max_llm_calls: 50
  max_runtime_seconds: 3600
  max_hypotheses_generated: 30

policy_tournament:
  max_policy_genomes: 1000
  max_simulations: 20000
  max_llm_calls: 500
  max_runtime_seconds: 21600
```

## Token counting

The LLM router must estimate tokens before calls and record actual usage after calls.

Fields to log:

```text
model_deployment
prompt_tokens_estimated
prompt_tokens_actual
completion_tokens_actual
call_latency_ms
cost_estimate_optional
workflow_name
agent_name
run_id
```

Even if Azure usage is already paid, usage must be tracked for operational control.

## Graceful degradation

When budget is constrained:

1. keep source checking,
2. defer low-priority extraction,
3. skip optional LLM summaries,
4. prefer deterministic parsers,
5. queue deep reasoning for next cycle.

Never silently exceed budget.
