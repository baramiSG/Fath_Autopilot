# 32 — Production Readiness Checklist

## Purpose

This is the final checklist before Fath Autopilot is allowed to run continuously on the government VM or be demonstrated as an autonomous system.

A checkbox is only complete if evidence exists: test output, smoke-test output, audit row, screenshot, or operator sign-off.

## 1. Architecture readiness

- [ ] Source Scout runs on Prefect schedule.
- [ ] Access Guard blocks inactive/manual-review sources.
- [ ] Crawlers write only to Raw Archive.
- [ ] Sanitizer produces UntrustedBlob objects.
- [ ] Extractors write only to Fact Store.
- [ ] Graph Builder writes only graph nodes/edges with provenance.
- [ ] Reasoning agents write hypotheses, not facts.
- [ ] Sanad is the only path to Insight Corpus.
- [ ] Fath Canvas renders from validated component specs only.

## 2. Public-data-only readiness

- [ ] No LMIS integration.
- [ ] No QNWIS integration.
- [ ] No ministry-private data.
- [ ] Source registry contains only approved public or licensed sources.
- [ ] Each active source has an onboarding checklist.
- [ ] Each active source has rate limits.
- [ ] Each active source has robots/terms review recorded.

## 3. Security readiness

- [ ] RBAC enabled in production.
- [ ] OIDC authentication enabled.
- [ ] No anonymous Canvas access except health endpoints.
- [ ] Approval policies seeded.
- [ ] Unauthorized approval attempts return 403.
- [ ] No unrestricted shell access for agents.
- [ ] Simulation sandbox has no network.
- [ ] TrustBoundary tests pass.
- [ ] Prompt-injection fixtures pass.
- [ ] Secrets are loaded from Key Vault or secure local equivalent.

## 4. Data integrity readiness

- [ ] Raw Archive is append-only.
- [ ] Raw Archive duplicate guard works.
- [ ] Fact status transitions are enforced.
- [ ] Quarantined facts excluded from retrieval and graph updates.
- [ ] Every fact has raw_archive_refs.
- [ ] Every graph edge has source_refs.
- [ ] Every insight has SanadValidationCard.
- [ ] Every prediction has resolution criteria or manual resolution type.

## 5. Event and UI readiness

- [ ] Redis Streams event bus running.
- [ ] Event schemas validate on emit and consume.
- [ ] DLQ works.
- [ ] UI Orchestrator maps events to component specs.
- [ ] Backend Pydantic validation rejects invalid specs.
- [ ] Frontend Zod validation rejects invalid specs.
- [ ] `RawArchiveRecordCard` renders.
- [ ] `WhatFathWantsToInvestigate` is first screen.
- [ ] `RunReplay` can reconstruct at least one heartbeat.

## 6. Evaluation readiness

- [ ] Golden datasets exist.
- [ ] Extraction eval meets thresholds.
- [ ] Retrieval eval meets thresholds.
- [ ] Graph eval meets thresholds.
- [ ] Sanad eval meets thresholds.
- [ ] Source-poisoning synthetic tests pass.
- [ ] Canvas schema tests pass.
- [ ] `make eval` produces EvalReport.

## 7. Operations readiness

- [ ] Docker Compose production override boots.
- [ ] Health and readiness endpoints pass.
- [ ] Prometheus metrics available.
- [ ] Structured logs include trace_id and run_id.
- [ ] Audit log verifier passes recent and full-chain check.
- [ ] Postgres backup succeeds.
- [ ] Object storage backup succeeds.
- [ ] Restore drill succeeds.
- [ ] Incident-report table exists.
- [ ] Operator runbooks tested.

## 8. Autonomy readiness

- [ ] Hourly heartbeat completes without manual intervention.
- [ ] Daily heartbeat completes without manual intervention.
- [ ] Biweekly Coverage Auditor proposes investigations.
- [ ] Weekly tournament runs only if evaluation gates pass.
- [ ] Level 5 external actions are blocked by default.
- [ ] All approval requests appear in Canvas.
- [ ] Budget circuit breakers work.
- [ ] Workflow resume from checkpoint works.

## 9. Demo readiness

The demo is ready only when the system can truthfully say:

```text
Fath ran unprompted for at least four weeks.
It checked public sources on schedule.
It archived raw evidence.
It extracted structured facts.
It built a legal-economic graph.
It proposed investigations on its own.
It rejected weak ideas.
It generated policy genomes.
It stress-tested them.
It validated survivors through Sanad.
It produced at least three credible insight cards.
It can replay every insight back to source evidence.
```

## 10. Kill criteria

Stop continuous operation immediately if any occurs:

- [ ] Audit chain verification fails.
- [ ] Access Guard allows a denied/manual-review source.
- [ ] Raw web content enters an LLM prompt outside TrustBoundary.
- [ ] Quarantined facts are used in retrieval or graph building.
- [ ] A source-poisoning critical signal affects a published insight.
- [ ] A workflow exceeds budget and continues anyway.
- [ ] An unauthorized user approves an action.
- [ ] Simulation sandbox accesses network.
- [ ] Fath Canvas renders unvalidated component JSON.

## Final operator sign-off

```text
Operator name:
Date:
Git commit:
Docs version:
Smoke tests passed:
Eval report ID:
Audit verification report ID:
Restore report ID:
Approved for continuous operation: yes/no
Notes:
```
