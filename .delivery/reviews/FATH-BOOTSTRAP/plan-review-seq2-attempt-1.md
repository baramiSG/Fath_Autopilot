# FATH-BOOTSTRAP — Independent Plan Review — Sequence 2, Attempt 1 of 3 (plan V4)

- Review type: Bootstrap, architecture, roadmap, bounded-task plan
- Project ID: `FATH_AUTOPILOT` · Scope: `FATH-BOOTSTRAP`
- Plan commit reviewed: `aaf09cc75ff9e10df3016f7749f2099128fb9f61`
- Reviewer: `PLAN_REVIEWER`, GPT-5.6 Sol (1M, Max, fast OFF, fresh read-only context)
- Review date: 2026-08-27
- Final governed outcome: **REJECT**
- Recorded by: controller (verbatim findings from the reviewer's handoff)

## Verified identities

All 11 plan-directory artifact hashes verified matching the state record (BOOTSTRAP_PLAN `d96b6c66...`, TASK-001_PLAN `d59634ff...`, PROPAGATION_MAP `43f029d4...`, V4_ADJUDICATION `196e3ce5...`, AUTHORITY_MANIFEST `c4b90b39...`, DOCUMENT_READ_ORDER `6976ccab...`, REQUIREMENTS_TRACEABILITY `f8b005af...`, PROJECT_MAP `1f6faf5f...`, ROADMAP `8c13a58e...`, REMEDIATION-1 `e54f99a0...`, REMEDIATION-2 `068a5c4c...`). AMENDMENT-002 verified at `af00923` committed alone, sha256 `0edb5245...`. Branch clean at exact commit through final recheck. Canonical docs 00–34 + README hashes matched the manifest. Reviewer also consulted official uv locking documentation for `--frozen` vs `--locked` semantics.

## Findings

### FATH-V4-001 — HIGH
- Affected: `TASK-001_PLAN.md` §§4.6–4.7, A4/A6; `PROPAGATION_MAP.md` PM-B1/B2. Basis: AMENDMENT-002 §§2–3.
- Observed: The plan declares `source_id` immutable and `slug` stable after activation, but defines no database/domain enforcement or negative verification. A PostgreSQL primary key alone remains updateable. Slug stability is not assigned to a tested owning task.
- Required condition: Define and verify the source-ID immutability invariant, and assign enforceable audited slug-change behavior before activation is introduced.

### FATH-V4-002 — HIGH
- Affected: `TASK-001_PLAN.md` §4.6, A4, implementation sequence step 6; `PROPAGATION_MAP.md` PM-B4. Basis: AMENDMENT-002 §13; Oracle Policy §§2, 5, 7, 18.
- Observed: Exact PostgreSQL mappings and normalized defaults are deferred to an implementer-authored future fixture; the plan even permits A4 to pin "whichever form the migration declares." Material expected results are not fixed by the reviewed plan. The FK proof is explicitly vacuous, and A4 does not establish numeric schema boundaries or the exact allowed application-table set.
- Required condition: Bind the complete expected schema before implementation, including exact types, defaults, constraints, boundaries, table set and applicable FK expectations, independently of migration output.

### FATH-V4-003 — HIGH
- Affected: `TASK-001_PLAN.md` §5, A12–A13. Basis: P3-003 required condition; Oracle Policy §§7, 11, 18, 37.
- Observed: `authoritative_source_literals.json` must contain authoritative literals but A13d requires every fixture to contain none. Migrations are excluded from the write-pattern scan; zero row counts cannot prove that a migration did not insert and later delete rows. A13a covers Tier-1/2 but omits doc-30 Tier-3 slugs despite claiming no seed content.
- Required condition: Remove the fixture contradiction and provide complete candidate-bound checks covering migration writes, all governed source identities, loader behavior, syntheticity and persistent final state.

### FATH-V4-004 — HIGH
- Affected: A1, A15, §4.9 and CI step 2. Basis: P3-002; official uv locking documentation; Oracle Policy §§5, 37.
- Observed: `uv sync --frozen` intentionally does not verify that `uv.lock` matches `pyproject.toml`; a stale lock can pass. A15 also checks only that direct dependencies are subsets of permitted lists, allowing required baseline dependencies to be omitted.
- Required condition: Distinguish required, optional and prohibited dependencies, verify positive completeness, and use a lock-freshness check such as `uv lock --check` or equivalent locked synchronization.

### FATH-V4-005 — HIGH
- Affected: A16 and CI step 4. Basis: P3-005; Constitution §7; Review Policy §14.
- Observed: `git diff --name-only` cannot prove that `.delivery/` paths are additions rather than modifications or deletions. `<PR base>` is neither an immutable SHA nor defined for push runs, so the comparison is not reproducibly candidate-bound.
- Required condition: Bind the comparison to an exact, governed base identity and inspect change status mechanically, including defined behavior for both push and PR events.

### FATH-V4-006 — HIGH
- Affected: implementation sequence step 9, §10, A10. Basis: Oracle Policy §§44–46; Review Policy candidate-identity requirements.
- Observed: The implementer must write all evidence under the candidate's `.delivery/` path before creating the candidate, but that evidence includes the CI URL/output for the candidate SHA — which cannot exist until after commit and CI execution. Committing it afterward changes the candidate SHA.
- Required condition: Separate committed pre-candidate evidence from post-commit CI/trusted artifacts and define retention without mutating the reviewed candidate.

### FATH-V4-007 — HIGH
- Affected: `PROPAGATION_MAP.md` provenance and graph sections. Basis: AMENDMENT-002 §12; docs 15, 27, 31, 32.
- Observed: Explicit provenance surfaces such as graph-edge `source_refs` and UI-card "source object IDs" are absent from the map. Their semantics are ambiguous, which is precisely why the mandatory full-corpus sweep must classify them. The doc-07 Python UUID/TypeScript serialized-UUID mapping itself is correct and uses no blanket `str` assumption.
- Required condition: Map every omitted source-reference surface, classify its semantics and owning task, and leave unresolved ambiguity OPEN rather than implicit.

### FATH-V4-008 — MEDIUM
- Affected: TASK-001 task contract. Basis: workspace control SG-TR-006.
- Observed: TASK-001 does not state the required data classification, although it constrains fixtures to synthetic data.
- Required condition: Add an explicit data classification and its handling restrictions.

### FATH-V4-009 — LOW
- Affected: plan metadata. Basis: artifact contents.
- Observed: V4 repeatedly calls the propagation map "69-surface," but PM-A1 through PM-N5 contain 79 mapped rows. `PROJECT_MAP.md` also retains the pre-amendment count of 35 canonical documents rather than 36 excluding the reference-only combined file.
- Required condition: Correct the audit/navigation counts.

## Prior-finding disposition

- P3-002: NOT RESOLVED (A2/A6/A14 improved; A4/A15 insufficient)
- P3-003: NOT RESOLVED (A12 improved; A13 internally contradictory, migration/content evasions)
- P3-004: RESOLVED
- P3-005: NOT RESOLVED (text reconciled; A16/evidence sequencing cannot enforce it)

## AMENDMENT-002 conformance

FAIL (incomplete): UUID/slug semantics, doc-29 FK correction, YAML rule, transport semantics and doc-07 UI mapping correctly represented; immutability/stability unverified, §12 propagation incomplete (provenance/graph surfaces), §13 oracle partial.

## TASK-001 oracle assessment

A1 PARTIAL · A2 VALID · A3 VALID · A4 PARTIAL · A5 VALID · A6 PARTIAL · A7 VALID · A8 VALID (scoped) · A9 VALID (scoped) · A10 PARTIAL · A11 VALID · A12 PARTIAL · A13 INVALID · A14 VALID · A15 INVALID · A16 INVALID

## Regression check

Gate truthfulness, GATE-SETUP-before-merge, A8 scope, Week-1 LLM classification, PG-image classification, ADR human-approval requirements, FA-OPEN-020 gating: preserved.

## Reviewer self-audit

Read-only maintained; no artifact edited or repaired. This is independent review evidence, not a formal trusted gate.
