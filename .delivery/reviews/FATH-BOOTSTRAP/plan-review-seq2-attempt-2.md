# FATH-BOOTSTRAP — Independent Plan Review — Sequence 2, Attempt 2 of 3 (plan V5)

- Review type: Bootstrap, architecture, roadmap, bounded-task plan
- Project ID: `FATH_AUTOPILOT` · Scope: `FATH-BOOTSTRAP`
- Plan commit reviewed: `b4e392d33e98250114c82d695b0decda951c0164`
- Reviewer: `PLAN_REVIEWER`, GPT-5.6 Sol (1M, Max, fast OFF, fresh read-only context)
- Review date: 2026-08-27
- Final governed outcome: **REJECT**
- Recorded by: controller (verbatim findings from the reviewer's handoff)

## Verified identities

All 12 plan-directory artifact hashes verified matching the state record (TASK-001_PLAN `0b4c23c4...`, BOOTSTRAP_PLAN `d64c7683...`, PROPAGATION_MAP `69874346...`, ROADMAP `ef04a774...`, REQUIREMENTS_TRACEABILITY `8f8faad3...`, PROJECT_MAP `387a90c9...`, REMEDIATION-3 `aa80c5b6...`, AUTHORITY_MANIFEST `c4b90b39...`, DOCUMENT_READ_ORDER `6976ccab...`, V4_ADJUDICATION `196e3ce5...`, REMEDIATION-1 `e54f99a0...`, REMEDIATION-2 `068a5c4c...`). Branch clean and unchanged; final identity recheck PASS. All 36 canonical documents read; all 37 manifest entries hash-matched; AMENDMENT-001/002 commits and hashes matched. uv semantics independently confirmed against official uv documentation.

## Findings

### FATH-V5-001 — HIGH
- Affected: `TASK-001_PLAN.md` §5 A13b, A13. Basis: Oracle Policy §§7, 11, 18, 37; FATH-V4-003.
- Observed: The migration regex still misses ordinary SQLAlchemy DML such as `op.execute(sa.insert(table).values(...))` followed by `op.execute(sa.delete(table))`. Both tested examples produced zero configured regex hits. Migrations are excluded from A13b-i, while A12 observes only final zero-row state.
- Required condition: Mechanically detect ordinary Alembic/SQLAlchemy INSERT, UPDATE and DELETE APIs, and prove through negative fixtures that an insert-then-delete migration fails.

### FATH-V5-002 — HIGH
- Affected: `TASK-001_PLAN.md` §6.0 indexes, A4. Basis: docs/03 indices; docs/34 §13; Oracle Policy §§2, 5, 7, 11.
- Observed: A4 pre-binds only the six index names. It does not bind or compare indexed columns, order, access method, predicate, or uniqueness. All four named indexes could target the wrong column and A4 would pass.
- Required condition: Pre-bind and mechanically compare each canonical index definition, not only its name.

### FATH-V5-003 — HIGH
- Affected: `TASK-001_PLAN.md` §4.9, A15. Basis: the plan's own pydantic v2 / sqlalchemy 2.x contract; Oracle Policy §§5, 37.
- Observed: A15 compares normalized package names only. It does not verify declared version constraints or resolved lockfile majors. `uv lock --check` proves consistency with project metadata, not that metadata requires the approved majors.
- Required condition: Verify applicable declared specifiers and resolved `uv.lock` versions, at minimum for Pydantic v2 and SQLAlchemy 2.x.

### FATH-V5-004 — MEDIUM
- Affected: `TASK-001_PLAN.md` §4.4; BOOTSTRAP_PLAN determinism rules. Basis: Oracle Policy §§44–45; Docker image-pinning guidance.
- Observed: `redis:7` is called "pinned," but Docker tags are mutable. The same candidate SHA can therefore execute against different Redis image contents.
- Required condition: Bind Redis to an immutable digest or explicitly narrow the reproducibility claim and retain the resolved digest as candidate evidence.

### FATH-V5-005 — LOW
- Affected: `REMEDIATION-3_ADJUDICATION.md` V4-002 disposition and control-state summary. Basis: actual §6.0 constraint list.
- Observed: The artifacts claim 15 named constraints. The exact list contains 13: six enum checks, five numeric checks, PK and UNIQUE.
- Required condition: Correct the constraint count without changing the actual 13-item schema contract.

## V4 finding disposition

- V4-001 RESOLVED · V4-002 PARTIALLY RESOLVED (index semantics missing) · V4-003 NOT RESOLVED (migration insert-then-delete mechanically possible) · V4-004 RESOLVED (V5-003 is a new version-enforcement gap) · V4-005 RESOLVED · V4-006 RESOLVED · V4-007 RESOLVED (84 unique rows; FA-OPEN-022/023 explicit) · V4-008 RESOLVED · V4-009 RESOLVED (V5-005 separate count defect)

## AMENDMENT-002 conformance

§§1–11 PASS · §12 PASS · §13 PARTIAL (index-definition oracle) · Overall: FAIL for advancement. Spot checks passed for the 33-column set, seven-value status enum/default, doc-03 enum values, conint(ge=0) boundaries, [0,1] confloat boundaries.

## TASK-001 oracle assessment

VALID: A1, A2, A3, A5–A12, A14, A16 · PARTIAL: A4 (index definitions), A15 (dependency versions) · INVALID: A13 (migration DML bypass). A10 valid only as candidate-controlled SHA-bound evidence. A12 validly proves final zero-row state but cannot repair A13's transient-write blind spot.

## Regression check

PASS: gate truthfulness and GATE-SETUP sequencing, A8 scope, Week-1 LLM posture as PROPOSED, PG-image classification, human-approved ADR requirement, FA-OPEN-020 gating, P3-004 anchored tree oracle. The mutable Redis tag is a new reproducibility defect (V5-004).

## Reviewer self-audit

Read-only maintained; independent review evidence, not a formal trusted gate.
