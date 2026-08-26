# 17 — Build Plan and Verification

## Six-week build plan

### Week 1 — Proactive substrate

Build:

- Source Registry
- Access Guard
- Qatar Open Data connector
- World Bank connector
- GDELT connector
- Al Meezan defined but inactive pending manual source review
- Raw Archive
- TrustBoundary + Sanitizer
- Event Bus
- Audit Log
- Fath Canvas v0

Verification:

- Source Scout checks approved sources.
- Access Guard records decisions.
- Raw records are archived with hashes.
- Events appear in Fath Canvas.
- UI leads with Investigation Queue, even if initially empty.

### Week 2 — Extraction and early graph

Build:

- Trust Boundary module
- Sanitizer
- Parser pipeline
- Economic indicator extractor
- Legal provision extractor
- Fact Store full implementation
- BGE-M3 embedding pipeline
- Initial Apache AGE graph

Verification:

- External content is wrapped as UntrustedBlob.
- Facts have evidence spans.
- Facts never contain hypotheses.
- Graph edges have provenance.

### Week 3 — Connection and autonomy

Build:

- Change Detector
- Anomaly Miner
- Connection Agent
- Coverage Auditor v0
- Investigation proposal workflow
- Fath Canvas Investigation Cards

Verification:

- System proposes at least three investigations unprompted.
- Each investigation has evidence and next action.
- Coverage Auditor rejects generic ideas.

### Week 4 — Policy genome and simulation

Build:

- Hypothesis Store
- Policy Genome Generator
- Scenario Runner v0
- Causal Skeptic
- Scenario Tournament UI

Verification:

- System generates structured policy genomes.
- Weak genomes are rejected.
- Tournament produces ranked candidates.

### Week 5 — Sanad, poisoning, calibration

Build:

- Sanad five-chain validator
- Source-Poisoning Detector
- Belief Calibration Store
- Run Replay
- Source Integrity Radar

Verification:

- Sanad validates or rejects candidate insights.
- Poisoning signals downgrade risky claims.
- Insights create belief records.
- Run replay works end to end.

### Week 6 — Autonomous briefing

Build:

- Insight Corpus
- Weekly briefing composer
- Final Fath Canvas demo flow
- Approval Marshal
- Human review flow

Verification:

- Weekly brief begins with what Fath wants to investigate.
- At least five unprompted investigations exist.
- At least three validated opportunity cards exist.
- At least one insight has full run replay.

## Verification checklist

### Security

- [ ] No crawler can call GPT-5.4.
- [ ] No raw web text enters prompt outside UntrustedBlob delimiter.
- [ ] No agent has unrestricted shell access.
- [ ] External actions are blocked.
- [ ] Access Guard rejects disallowed sources.
- [ ] Injection fixtures pass.

### Data integrity

- [ ] Raw Archive records are immutable.
- [ ] Duplicate content hashes are not reinserted.
- [ ] Supersession preserves old records.
- [ ] Fact Store records have provenance.
- [ ] Hypotheses are separate from facts.

### Events and UI

- [ ] Every agent emits events.
- [ ] Event payloads validate.
- [ ] Dead-letter handling works.
- [ ] Fath Canvas rejects invalid component specs.
- [ ] Run replay reconstructs event path.

### Reasoning

- [ ] Connection Agent uses graph + embeddings + verification.
- [ ] Coverage Auditor uses Al-Muhāsibī.
- [ ] Sanad source grounding requires passages.
- [ ] Numerical validation uses deterministic checks.
- [ ] Red-team dissent is recorded.

### Evolution

- [ ] Insight predictions create Belief Calibration records.
- [ ] Due beliefs are checked.
- [ ] Calibration errors are recorded.
- [ ] Source reliability can be adjusted through calibration only.

## Exit criterion for first sovereign demo

Do not pitch the concept alone. Pitch the observed behavior after 4–6 weeks of operation:

```text
This is what Fath discovered unprompted using only public data.
```
