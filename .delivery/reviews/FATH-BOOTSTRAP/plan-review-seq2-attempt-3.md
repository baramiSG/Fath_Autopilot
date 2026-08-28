# FATH-BOOTSTRAP — Independent Plan Review — Sequence 2, Attempt 3 of 3 (plan V6) — FINAL

- Review type: Bootstrap, architecture, roadmap, bounded-task plan
- Project ID: `FATH_AUTOPILOT` · Scope: `FATH-BOOTSTRAP`
- Plan commit reviewed: `d019b2e81a2561bfea72d58620e2fefadbefbb14`
- Reviewer: `PLAN_REVIEWER`, GPT-5.6 Sol (1M, Max, fast OFF, fresh read-only local-only context)
- Review date: 2026-08-27
- Final governed outcome: **REJECT** — sequence-2 ladder exhausted; scope enters `BLOCKED_FOR_SALIM`
- Recorded by: controller (verbatim findings from the reviewer's handoff)

## Verified identities

All 13 plan-directory artifact hashes verified matching the state record (TASK-001_PLAN `4f57d2d8...`, BOOTSTRAP_PLAN `27ca0f5d...`, PROPAGATION_MAP `db36dad7...`, PROJECT_MAP `e864b17a...`, REMEDIATION-3 `19d59005...`, REMEDIATION-4 `f36c4a0d...`, ROADMAP `ef04a774...`, REQUIREMENTS_TRACEABILITY `8f8faad3...`, AUTHORITY_MANIFEST `c4b90b39...`, DOCUMENT_READ_ORDER `6976ccab...` [reviewer recomputed correctly; one transcription omission in its report noted and disclosed by the reviewer itself], V4_ADJUDICATION `196e3ce5...`, REMEDIATION-1 `e54f99a0...`, REMEDIATION-2 `068a5c4c...`). AMENDMENT-001/002 hashes matched. HEAD, branch, clean status unchanged through final recheck. All 37 manifest entries hash-matched; docs 00–34 + README read.

## Findings

### FATH-V6-001 — HIGH (classified BLOCKER-B7 by reviewer)
- Affected: `TASK-001_PLAN.md` §5 A13b-ii/R1–R4 and A13; `REMEDIATION-4_ADJUDICATION.md`. Basis: Oracle Policy §§2, 5, 7, 11, 37; V5-001 required condition.
- Observed: Direct `op.execute(sa.insert(...))` / `op.execute(sa.delete(...))` and direct f-strings are now caught. However R1/R2 recognize only direct `op.<attribute>` calls, R3 does not prohibit dynamic attribute lookup, and R4 scans only complete DML patterns in individual literals. This equivalent DML passes all stated rules: `getattr(op, "execute")(getattr(sa, "insert")(table).values(value=1))` (and the delete form). An indirect f-string using `verb = "INSERT"` avoids R4 because the keyword and ` INTO` occupy separate AST literals. Alias resolution is not specified. Reviewer executed the stated predicates locally: named fixture caught; getattr/aliased-import/indirect-f-string variants NOT caught; legitimate `CREATE FUNCTION`/`CREATE TRIGGER ... BEFORE UPDATE ON` strings passed without false positives. The six negative fixtures are valid oracles for those six specimens, not for the broader zero-DML claim.
- Required condition: Bind handling of aliases and execution sinks, reject dynamic attribute/call indirection and dynamically assembled SQL where applicable, and add negative fixtures proving these equivalent INSERT/UPDATE/DELETE paths fail without rejecting the legitimate trigger/function DDL.

### FATH-V6-002 — MEDIUM
- Affected: `TASK-001_PLAN.md` §4.4; `BOOTSTRAP_PLAN.md` §§4.4/6; `REMEDIATION-4_ADJUDICATION.md`. Basis: the plan's reproducibility claim; Oracle Policy §§44–45.
- Observed: Redis, Actions, and gitleaks are now immutably bound, but AGE and pgvector remain pinned only by release tags. Git tags can be replaced, so identical candidate content can still retrieve different extension source. This contradicts the adjudication claim that no other mutable tags remain.
- Required condition: Bind extension source to immutable commits or checksum-verified archives, or narrow the reproducibility claim explicitly.

### FATH-V6-003 — LOW
- Affected: V6 cross-references and durable state metadata. Basis: exact artifact contents.
- Observed: `TASK-001_PLAN.md` still cites `BOOTSTRAP_PLAN.md (v5)`; `BOOTSTRAP_PLAN.md` still cites `TASK-001_PLAN.md v5`; control-plane `BUILD_STATE.yaml` still records "15 constraints" in its V5 summary.
- Required condition: Correct the active V6 references and append an accurate 13-constraint correction to durable state without erasing review history.

## V5 finding disposition

- V5-001: PARTIALLY RESOLVED (direct forms caught; dynamic/aliased equivalents remain)
- V5-002: RESOLVED (all six index definitions match docs/03 and AMENDMENT-002)
- V5-003: RESOLVED (declarations and resolved majors enforced)
- V5-004: Redis RESOLVED; same-class AGE/pgvector tag gap = FATH-V6-002
- V5-005: schema resolved at 13; stale durable-state metadata remains

## AMENDMENT-002 conformance

§§1–11 PASS · §12 PASS (84 rows independently counted) · §13 PASS (index definitions sufficiently pre-bound) · **Overall: PASS**

## TASK-001 oracle assessment

A1–A12, A14–A16 VALID (A8/A9 scoped; A10 SHA-bound candidate evidence only; A12 observed states only) · A13 PARTIAL

## Regression and boundedness

All previously resolved findings preserved (gate truthfulness, GATE-SETUP sequencing, A8 scope, Week-1 LLM posture, ADR human-approval, FA-OPEN-020 governance, anchored tree oracle, source-ID immutability, governed-base diff, evidence retention, 84-row propagation, data classification). TASK-001 remains coherently bounded and generally implementable; the blocking defect is the material partial oracle for the explicit zero-DML acceptance claim.

## Reviewer self-audit

PASS — read-only maintained; no artifact repaired; no unspecified detector behavior credited. Review is evidence, not a formal trusted gate. Reviewer states: this rejection exhausts review sequence 2 and requires the controller to transition the scope to BLOCKED_FOR_SALIM.
