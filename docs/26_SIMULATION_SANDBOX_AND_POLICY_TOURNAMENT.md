# 26 — Simulation Sandbox and Policy Tournament

## Purpose

The policy tournament is where Fath moves from research to economic decision intelligence. It stress-tests policy genomes against uncertainty and ranks them by expected impact, downside risk, robustness, and implementation feasibility.

This document locks the first production implementation: **template-based simulations only**. No arbitrary LLM-generated code executes in the production path until sandbox certification passes.

## Policy tournament lifecycle

```text
HypothesisGenerated
   ↓
PolicyGenomeProposed
   ↓
Scenario parameter set generated
   ↓
Simulation template selected
   ↓
Latin hypercube samples generated
   ↓
Policy genomes simulated across futures
   ↓
Dominated genomes eliminated
   ↓
Survivors ranked
   ↓
ScenarioRunCompleted event emitted
   ↓
Sanad validation begins
```

## Core schemas

```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID

UncertaintyDimension = Literal[
    "lng_price",
    "global_interest_rate",
    "regional_fdi_competition",
    "investor_risk_appetite",
    "regulatory_execution_speed",
    "talent_availability_public_benchmark",
    "trade_disruption",
    "geopolitical_risk",
    "technology_adoption_speed",
]

class ScenarioParameter(BaseModel):
    name: UncertaintyDimension
    low: float
    high: float
    distribution: Literal["uniform", "triangular", "normal", "lognormal"]
    unit: str
    source_fact_ids: list[UUID] = Field(default_factory=list)

class ScenarioSample(BaseModel):
    sample_id: UUID
    seed: int
    parameters: dict[str, float]

class SimulationTemplate(BaseModel):
    template_id: str
    name: str
    supported_policy_kinds: list[str]
    required_inputs: list[str]
    output_metrics: list[str]
    version: str

class PolicyGenomeSimulationInput(BaseModel):
    policy_genome_id: UUID
    target_sector_id: UUID
    levers: list[dict]
    estimated_cost_usd: float | None = None
    time_horizon_months: int
    target_indicators: list[UUID]
    implementation_difficulty: Literal["low", "medium", "high"]

class PolicyGenomeSimulationResult(BaseModel):
    policy_genome_id: UUID
    scenario_run_id: UUID
    samples_run: int
    expected_impact_mean: float
    impact_5th_percentile: float
    impact_95th_percentile: float
    downside_risk_score: float = Field(ge=0, le=1)
    robustness_score: float = Field(ge=0, le=1)
    implementation_penalty: float = Field(ge=0, le=1)
    final_score: float = Field(ge=0, le=1)
    dominated: bool
    survivor: bool
    metric_unit: str
    run_metadata: dict = Field(default_factory=dict)
```

## Simulation templates in the first build

### 1. FDI conversion template

Use for policy genomes targeting foreign investment conversion.

```text
Inputs:
- baseline FDI projects by sector
- regional benchmark FDI project activity
- policy lever intensity
- regulatory execution speed
- investor risk appetite
- regional competition

Outputs:
- expected additional FDI projects
- expected capex range
- time-to-effect
- downside risk
```

Simplified scoring model:

```python
def fdi_conversion_effect(base_gap, lever_strength, execution_speed, investor_appetite, regional_competition):
    raw = base_gap * lever_strength * execution_speed * investor_appetite
    competition_penalty = 1.0 - (0.35 * regional_competition)
    return max(0.0, raw * competition_penalty)
```

### 2. Import-substitution template

Use for HS-category opportunities.

```text
Inputs:
- import value and growth
- supplier concentration
- domestic business density proxy
- infrastructure fit
- legal feasibility
- regional demand

Outputs:
- local value capture potential
- re-export potential
- risk of uneconomic substitution
```

### 3. Regulatory-friction template

Use for legal/economic bottleneck hypotheses.

```text
Inputs:
- affected business activities
- number of legal constraints
- comparable regional policy openness
- firm density trend
- sector growth trend

Outputs:
- reform leverage score
- implementation difficulty
- expected activity formation impact
```

### 4. Productivity-frontier template

Use for productivity or sector efficiency hypotheses.

```text
Inputs:
- value-added per worker public benchmarks
- wage / productivity ratios
- technology adoption signals
- company disclosure signals
- policy lever intensity

Outputs:
- productivity uplift range
- time-to-effect
- workforce adjustment risk
```

## Scenario sampling

Use Latin Hypercube Sampling.

```python
from scipy.stats import qmc

class ScenarioSampler:
    def sample(self, dimensions: list[ScenarioParameter], n: int, seed: int) -> list[ScenarioSample]:
        sampler = qmc.LatinHypercube(d=len(dimensions), seed=seed)
        unit_samples = sampler.random(n=n)
        scaled = qmc.scale(
            unit_samples,
            [d.low for d in dimensions],
            [d.high for d in dimensions],
        )
        return [
            ScenarioSample(
                sample_id=uuid4(),
                seed=seed,
                parameters={d.name: float(scaled[i][j]) for j, d in enumerate(dimensions)},
            )
            for i in range(n)
        ]
```

Default first-build sample count:

```text
n = 200 samples per policy genome
```

Weekly tournament can increase to 1,000 once runtime is measured.

## Ranking formula

```python
def final_policy_score(
    expected_impact_norm: float,
    robustness_score: float,
    downside_risk_score: float,
    implementation_penalty: float,
    evidence_confidence: float,
) -> float:
    return (
        0.35 * expected_impact_norm
        + 0.25 * robustness_score
        + 0.20 * (1.0 - downside_risk_score)
        + 0.10 * (1.0 - implementation_penalty)
        + 0.10 * evidence_confidence
    )
```

All components are normalized to `[0, 1]` within the tournament batch.

## Dominance rule

Policy genome A dominates B if:

```text
A expected impact >= B expected impact
A downside risk <= B downside risk
A implementation difficulty <= B implementation difficulty
A confidence >= B confidence
and at least two of these are strictly better
```

Dominated genomes are eliminated unless their Al-Muhāsibī novelty score is at least 9.0, in which case they are retained for human review as unconventional candidates.

## Sandbox requirements

First production implementation uses reviewed templates, but simulation still runs inside a restricted container.

```yaml
simulation-sandbox:
  image: fath/simulation-sandbox:latest
  network_mode: "none"
  read_only: true
  mem_limit: 16g
  cpus: "8"
  pids_limit: 512
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  volumes:
    - ./simulation_inputs:/inputs:ro
    - ./simulation_outputs:/outputs:rw
```

Allowed imports inside sandbox:

```text
numpy
pandas
scipy
mesa
simpy
networkx
statsmodels
sklearn
```

Blocked:

```text
requests
httpx
urllib
socket
subprocess
os.system
pathlib writes outside /outputs
```

## Reproducibility

Every run records:

```text
simulation_template_id
simulation_template_version
policy_genome_id
scenario_run_id
random_seed
sample_count
input_fact_ids
input_hash
output_hash
started_at
completed_at
container_image_digest
```

```sql
CREATE TABLE scenario_runs (
    scenario_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_genome_id UUID NOT NULL,
    simulation_template_id TEXT NOT NULL,
    simulation_template_version TEXT NOT NULL,
    random_seed INTEGER NOT NULL,
    sample_count INTEGER NOT NULL,
    input_fact_ids UUID[] NOT NULL DEFAULT '{}',
    input_hash TEXT NOT NULL,
    output_hash TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    container_image_digest TEXT NOT NULL,
    results JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

## Certification for LLM-generated code

LLM-generated simulation code is not allowed in production until all conditions are met:

1. Code executes only inside no-network sandbox.
2. Static analysis passes: no blocked imports, no file writes outside `/outputs`, no subprocess, no sockets.
3. Unit tests generated and executed.
4. Determinism test passes: same seed → same result.
5. Resource limit test passes.
6. Human operator approves template promotion.
7. Audit row records exact code hash and approval.

Until then, GPT-5.4 may propose simulation designs, but Engineer must translate them into reviewed templates manually.

## Test fixtures

`tests/simulation/test_policy_tournament.py` must include:

1. Latin hypercube sampler produces bounded values.
2. Same seed produces identical samples.
3. FDI conversion template returns non-negative results.
4. Dominance rule eliminates dominated genomes.
5. Novelty exception retains dominated but high-novelty genome.
6. Final score is in `[0,1]`.
7. Sandbox blocks network calls.
8. Sandbox blocks subprocess.
9. Scenario run records input and output hashes.
