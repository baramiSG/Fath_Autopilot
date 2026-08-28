# FATH-BOOTSTRAP — Independent Plan Review — Attempt 1 of 3

- Review type: Bootstrap/architecture, roadmap, and bounded-task plan
- Project ID: `FATH_AUTOPILOT`
- Scope ID: `FATH-BOOTSTRAP`
- Plan path: `.delivery/plans/FATH-BOOTSTRAP/`
- Plan commit reviewed: `3735813b4c7cddd41ac9251623fabbe505f3d298`
- Reviewer role: `PLAN_REVIEWER`
- Reviewer model: `GPT-5.6 Sol` (context 1M, reasoning Max, fast OFF, read-only, fresh context)
- Review date: 2026-08-26
- Final governed outcome: **REJECT**
- Recorded by: controller (verbatim findings from the reviewer's handoff)

## Verified identities

- `BOOTSTRAP_PLAN.md`: `c945742ea49c4331a31f40645257c444fb4db3fe5cfcf56df85f65495a45aa6c`
- `ROADMAP.md`: `cfbcf7c0b4879307fd1ed34547ac8c688ef81b5a6af4ae068884c5a4cc258972`
- `TASK-001_PLAN.md`: `fbccd528d3c787f9e176023f651e9d530729f1d4020c63c8edbb650066b22a20`
- AMENDMENT-001 commit verified: `234a24d9e012710352d35aa5b1314a6395614945` (doc 33 hash `3ea00519a4e7b79adb2e1f60afcfd4c393906033c148fd254fb1d71e15c61589`)
- Governance hashes matched frozen baseline; branch clean and byte-identical at the exact commit throughout review.

## Authority inspected (per reviewer)

Control-plane governance (all six documents) + `BUILD_STATE.yaml`; canonical project documents `docs/00`–`docs/33` and `docs/README.md`; all seven planning/navigation artifacts; sampled authority hashes matched the manifest.

## Findings

### FATH-PR-001 — BLOCKER
- Affected: `BOOTSTRAP_PLAN.md` §§2, 12; `TASK-001_PLAN.md` §§4, 6, 8; Week-1 roadmap.
- Basis: docs 03, 24, 29, 30.
- Observed: The task requires an exact 16-record seed set but authority does not provide complete required values such as base URLs and reliability tiers. Doc 03 uses UUID `source_id`; docs 29/30 use textual IDs. The plan does not reconcile this. It also marks three sources active without assigning the mandatory onboarding checklists required before activation. A5/A6 could pass with materially invented or incorrect seed records.
- Required condition: Establish an authoritative, approved full seed mapping and identifier model, define idempotency identity, assign onboarding evidence before activation, and compare the complete persisted records against that oracle. Otherwise record the scope as authority-blocked.

### FATH-PR-002 — HIGH
- Affected: `TASK-001_PLAN.md` §§4.1, 4.6, 10.
- Basis: doc 16 canonical layout; doc 23 anti-drift rule.
- Observed: The task introduces `sources/`, `trust/`, singular `budget/`, and `audit/`, while doc 16 specifies `safety/`, `budgets/`, and different ownership. It also places migrations/tests outside doc 16's canonical locations while claiming exact compliance. No acceptance criterion verifies the required layout.
- Required condition: Use canonical paths or obtain the required human-approved ADR for deviations, then add an exact layout/boundary oracle.

### FATH-PR-003 — HIGH
- Affected: `TASK-001_PLAN.md` §6, especially A8–A9.
- Basis: AMENDMENT-001 verifier scope; Oracle Policy §§4, 7, 22, 37.
- Observed: A8 requires a repository-wide absence of "A100" and "Azure OpenAI", but canonical historical documents necessarily contain those terms. It is therefore impossible as written and broader than AMENDMENT-001, which restricts implementation/configuration/sizing artifacts. A9's repository-wide "no secret" claim is supported only by inspection and a gitignore test, not a defined secret-scanning oracle.
- Required condition: Scope A8 to prohibited implementation/configuration artifacts with explicit exclusions, and replace A9 with a precise candidate-scoped claim plus an independently configured secret scan.

### FATH-PR-004 — HIGH
- Affected: `BOOTSTRAP_PLAN.md` §4.3; `ROADMAP.md` Weeks 1–2.
- Basis: docs 07, 14, 18 and AMENDMENT-001.
- Observed: The plan classifies the entire Week-1 pipeline as necessarily zero-LLM based on the hourly heartbeat's `max_llm_calls: 0`; doc 14 permits 200 calls for daily ingestion, while docs 07/18 define model-produced UI specs and retry behavior. The provider-agnostic client is deferred to Week 2 although Week-1 UI planning retains model-retry semantics.
- Required condition: Mark deterministic Week-1 UI/extraction as a proposal and define it explicitly, or schedule the provider-agnostic client before any Week-1 model call. Align dependencies and acceptance criteria accordingly.

### FATH-PR-005 — MEDIUM
- Affected: `BOOTSTRAP_PLAN.md` §4.3; `TASK-001_PLAN.md` §4.4.
- Basis: docs 02, 22, 28.
- Observed: A custom PG16 image compiling AGE and pgvector is labelled `DERIVED`. Authority requires one PG16 instance with those extensions, but does not require this packaging method. Extension versions are also delegated to implementation.
- Required condition: Reclassify the image strategy as `PROPOSED`, identify reproducible version-selection constraints, and define functional extension checks.

### FATH-PR-006 — HIGH
- Affected: `BOOTSTRAP_PLAN.md` §§4.2, 9; traceability `FA-REQ-CP-001`.
- Basis: Review and Acceptance Policy §§36–39; current `BUILD_STATE.yaml`.
- Observed: Candidate-controlled GitHub Actions is described as trusted verification, while protected CI, branch protection, and formal receipts are all unconfigured. The plan later acknowledges that no trusted-receipt claim can be made, creating an internal classification conflict.
- Required condition: Treat TASK-001 CI as SHA-bound test evidence until an external protected mechanism is configured; do not label it a trusted gate beforehand.

### FATH-PR-007 — MEDIUM
- Affected: `REQUIREMENTS_TRACEABILITY.json` `FA-REQ-W5-001`, `FA-OPEN-004`.
- Basis: AMENDMENT-001 "Flagged OPEN"; doc 23 anti-drift rule.
- Observed: `FA-REQ-W5-001` still presents Entra OIDC as specified production authentication, although AMENDMENT-001 makes the production provider OPEN. The module-path resolution says the planner will create an ADR but omits doc 23's required human approval.
- Required condition: Mark production authentication as OPEN, cite doc 33, and require explicit human approval for authority-changing ADRs.

## Reviewer self-audit

Reviewer reported: authority independently inspected, no files changed, no repair or self-approval performed. This review is evidence only, not the formal trusted gate.
