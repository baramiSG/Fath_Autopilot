# 12 — Source Poisoning and Narrative Defense

## Purpose

Prompt injection defends against malicious instructions. Source-poisoning defense defends against manipulated facts, coordinated narratives, citation loops, and artificial consensus.

Assume that if Fath becomes influential, adversaries may try to affect public sources to influence policy conclusions.

## Threat classes

1. Coordinated news narratives.
2. Citation loops across weak sources.
3. Planted sector reports.
4. Manipulated public commentary.
5. Sudden convergence without primary evidence.
6. Synthetic repetition across apparently separate outlets.
7. Compromised or altered public pages.
8. False benchmark-country comparisons.

## Claim extraction

Every report/news/policy claim should create a claim candidate:

```python
class ClaimCandidate(BaseModel):
    claim_id: UUID
    normalized_claim: str
    claim_type: str
    source_id: UUID
    raw_id: UUID
    published_at: Optional[datetime]
    retrieved_at: datetime
    entities: list[str]
    sectors: list[str]
    countries: list[str]
    supporting_text_hash: str
```

## Claim clustering

```python
class ClaimCluster(BaseModel):
    claim_cluster_id: UUID
    canonical_claim: str
    claim_ids: list[UUID]
    first_seen_at: datetime
    last_seen_at: datetime
    source_ids: list[UUID]
    independence_groups: list[str]
    wording_similarity_score: float
    primary_evidence_count: int
    poisoning_risk_score: float
```

## Algorithm 1 — Wording similarity via MinHash + Jaccard

Parameters:

```text
shingle size: 5 tokens
minhash permutations: 128
candidate Jaccard threshold: 0.82
near-duplicate threshold: 0.90
```

Process:

```text
1. Normalize claim text.
2. Create 5-token shingles.
3. Compute MinHash signature.
4. Use LSH to find candidate similar claims.
5. Compute exact Jaccard for candidates.
6. Cluster claims above 0.82.
7. Mark near-duplicate wording above 0.90.
```

High similarity across supposedly independent sources is a risk signal, especially if timing is tight.

## Algorithm 2 — Citation loop detection

Build a citation subgraph:

```text
source/article A cites source/article B
source/article B cites source/article C
source/article C cites source/article A
```

Use graph cycle detection.

Risk increases when:

- a claim has many sources but few original primary references,
- sources cite each other circularly,
- all roads lead to one weak origin,
- no primary indicator supports the claim.

Pseudocode:

```text
for claim_cluster in clusters:
    citation_graph = build_citation_graph(claim_cluster.claim_ids)
    cycles = find_cycles(citation_graph)
    primary_roots = count_primary_sources(citation_graph)
    if cycles and primary_roots == 0:
        flag citation_loop_risk
```

## Algorithm 3 — Convergence without primary evidence

Parameters:

```text
short window: 72 hours
medium window: 7 days
primary indicator lookback: 30 days
minimum sources for convergence: 4
minimum independence groups: 2
```

Process:

```text
1. Detect rapid emergence of similar claim cluster.
2. Check whether primary indicators moved in same direction.
3. Check whether official datasets or filings support the claim.
4. If narratives converge but primary indicators do not, flag risk.
```

Example:

```text
Claim cluster: Qatar logistics competitiveness is declining.
News convergence: 6 sources in 72 hours.
Primary indicators: no change in trade throughput, port metrics, or investment announcements.
Risk: convergence without primary evidence.
```

## Risk scoring

```text
poisoning_risk_score =
  0.25 * wording_similarity_risk
+ 0.25 * citation_loop_risk
+ 0.20 * convergence_without_primary_evidence
+ 0.15 * source_independence_weakness
+ 0.10 * timing_anomaly
+ 0.05 * historical_source_unreliability
```

Thresholds:

```text
>= 0.80 → quarantine claim cluster
0.60–0.79 → require corroboration before use
0.40–0.59 → downgrade confidence
< 0.40 → normal handling
```

## Source-poisoning event

Emit `poisoning_signal_detected` when risk >= 0.60.

## Impact on Sanad

If a target insight depends on a claim cluster with poisoning risk >= 0.60:

- source grounding cannot be PASS unless independent primary evidence exists,
- adversarial red-team must record dissent,
- Fath Canvas must show Source Integrity Radar.

## Human review

Human review is required for:

- poisoning risk >= 0.80,
- any high-impact insight relying on news/event claims,
- any claim where source independence cannot be established.
