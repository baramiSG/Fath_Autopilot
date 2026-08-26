# 11 — Sanad Validation Specification

## Purpose

Sanad is the validation layer. It determines whether a candidate hypothesis, policy genome, or insight is sufficiently grounded, coherent, plausible, adversarially resilient, and executable to be promoted.

## Five chains

1. Source grounding
2. Numerical consistency
3. Causal plausibility
4. Adversarial red-team
5. Execution feasibility

## Sanad validation record

```python
class SanadVerdict(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"

class SanadChainResult(BaseModel):
    chain_name: str
    verdict: SanadVerdict
    score: float
    summary: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    failure_reasons: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

class SanadValidationRecord(BaseModel):
    sanad_validation_id: UUID
    target_object_type: str
    target_object_id: UUID
    source_grounding: SanadChainResult
    numerical_consistency: SanadChainResult
    causal_plausibility: SanadChainResult
    adversarial_red_team: SanadChainResult
    execution_feasibility: SanadChainResult
    overall_score: float
    confidence_tier: str
    dissent_recorded: bool
    promotion_allowed: bool
    created_at: datetime
```

---

# Chain 1 — Source grounding

## Algorithm

```text
1. Extract all factual claims from the target object.
2. For each claim, run retrieval over Fact Store and relevant raw chunks.
3. Require at least 3 supporting passages for high-confidence claims.
4. Require at least 2 independent sources for high-confidence claims.
5. Check contradiction candidates.
6. Assign claim-level grounding scores.
7. Aggregate to chain score.
```

## Retrieval thresholds

```text
Top K per claim: 20
Minimum passage cosine similarity: 0.72
Strong support: similarity >= 0.80 and source is primary/official
Weak support: 0.72–0.79 or secondary/institutional source
News-only support maximum verdict: PARTIAL
No support: FAIL
```

## Aggregation

```text
source_grounding_score =
  average(claim_grounding_scores) * source_diversity_multiplier - contradiction_penalty
```

Verdict:

```text
>= 0.80 PASS
0.55–0.79 PARTIAL
< 0.55 FAIL
```

---

# Chain 2 — Numerical consistency

## Deterministic checks

Use Python predicates before LLM interpretation.

Required checks:

1. Unit compatibility.
2. Currency conversion sanity.
3. Date/time-period alignment.
4. Range plausibility.
5. Stock-flow reconciliation where applicable.
6. Percentages sum sanity where applicable.
7. Growth-rate recomputation.
8. Import/export balance sanity.
9. Duplicate denominator detection.
10. Base-year mismatch detection.

## Predicate interface

```python
class NumericalCheckResult(BaseModel):
    check_name: str
    passed: bool
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    affected_claims: list[str] = Field(default_factory=list)

class NumericalValidationInput(BaseModel):
    target_object_id: UUID
    extracted_numbers: list[dict]
    source_fact_ids: list[UUID]
```

## Examples

```python
def check_percentage_range(value: float) -> bool:
    return 0 <= value <= 100

def check_growth_rate(previous: float, current: float, claimed_growth: float, tolerance: float = 0.02) -> bool:
    computed = (current - previous) / previous
    return abs(computed - claimed_growth) <= tolerance
```

Verdict:

```text
Critical failed check → FAIL
High severity failures > 1 → FAIL
Medium failures with explainable assumptions → PARTIAL
All critical/high checks pass → PASS
```

---

# Chain 3 — Causal plausibility

## Purpose

Determine whether the proposed mechanism plausibly links intervention to expected outcome.

## Pipeline

```text
1. Extract causal mechanism from hypothesis/policy genome.
2. Retrieve historical analogs from Insight Corpus, Fact Store, and benchmark country corpus.
3. Score analog similarity.
4. Check whether mechanism has at least 2 plausible precedent supports or strong structural logic.
5. Search for contradictory analogs.
6. Run Causal Skeptic prompt.
7. Produce causal plausibility score.
```

## Historical analog score

```text
analog_score =
  0.25 * sector_similarity
+ 0.20 * policy_lever_similarity
+ 0.20 * country_context_similarity
+ 0.15 * time_horizon_similarity
+ 0.10 * institution_similarity
+ 0.10 * outcome_similarity
```

Thresholds:

```text
analog_score >= 0.70 → strong analog
0.50–0.69 → weak analog
< 0.50 → not counted
```

Minimum precedent count:

```text
PASS: at least 2 strong analogs or 1 strong analog + strong causal structure
PARTIAL: 1 strong analog or 2 weak analogs
FAIL: no analog and weak causal structure
```

---

# Chain 4 — Adversarial red-team

## Prompt template

```text
You are the Sanad Adversarial Red-Team.

Your task is to attack the candidate insight. Do not improve it. Do not make it sound balanced. Try to disprove it.

Evaluate:
1. Hidden assumptions
2. Missing evidence
3. Causal failure modes
4. Legal or institutional blockers
5. Regional competitor responses
6. Unintended consequences
7. Source-poisoning or narrative manipulation risks
8. What would prove this wrong

Return JSON only.
```

## Output schema

```python
class RedTeamFinding(BaseModel):
    finding_id: UUID
    severity: Literal["low", "medium", "high", "critical"]
    finding_type: str
    description: str
    evidence_needed: Optional[str] = None
    disconfirmation_test: Optional[str] = None

class RedTeamOutput(BaseModel):
    target_object_id: UUID
    findings: list[RedTeamFinding]
    overall_resilience_score: float
    dissent_required: bool
    summary: str
```

## Dissent criteria

Record dissent if:

- any critical finding remains unresolved,
- overall resilience score < 0.60,
- key causal assumption lacks supporting evidence,
- source poisoning risk > 0.70,
- execution feasibility is unclear.

---

# Chain 5 — Execution feasibility

## Boundary

Use deterministic rule registry first. Use GPT-5.4 only for structured assessment where rules do not cover the case.

## Rule registry path

Store rules in:

```text
src/fath/validators/execution_rules.yaml
```

Rule examples:

```yaml
- id: REQUIRES_LEGAL_CHANGE
  condition: "policy_lever.legal_change_required == true"
  effect: "implementation_difficulty += 0.25"

- id: MULTI_MINISTRY_DEPENDENCY
  condition: "len(owner_entities) >= 3"
  effect: "execution_risk += 0.20"

- id: NO_CLEAR_OWNER
  condition: "owner_entity is null"
  effect: "verdict = partial"
```

## LLM scoring path

Use only after deterministic rules produce an initial score. GPT-5.4 may assess:

- institutional complexity,
- sequencing difficulty,
- stakeholder resistance,
- pilotability,
- evidence sufficiency.

## Feasibility scoring

```text
execution_feasibility_score =
  0.25 * legal_feasibility
+ 0.20 * institutional_owner_clarity
+ 0.20 * pilotability
+ 0.15 * implementation_speed
+ 0.10 * data_availability
+ 0.10 * risk_controllability
```

Verdict:

```text
>= 0.75 PASS
0.50–0.74 PARTIAL
< 0.50 FAIL
```

## Promotion rule

An insight can be `BRIEFING_READY` only if:

```text
source_grounding != FAIL
numerical_consistency != FAIL
causal_plausibility != FAIL
execution_feasibility != FAIL
overall_score >= 0.65
```

If adversarial dissent is recorded, the insight may still be briefed but must show dissent prominently.
