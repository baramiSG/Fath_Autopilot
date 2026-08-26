# FATH-BOOTSTRAP — Independent Plan Review — Attempt 2 of 3

- Review type: Bootstrap, architecture, roadmap, and bounded-task plan
- Project ID: `FATH_AUTOPILOT`
- Scope ID: `FATH-BOOTSTRAP`
- Plan path: `.delivery/plans/FATH-BOOTSTRAP/`
- Branch: `plan/bootstrap-and-task-001`
- Plan commit reviewed: `77b08242d624bbb4bbe4f91553209cdee201fb48`
- Reviewer role: `PLAN_REVIEWER`
- Reviewer model: `GPT-5.6 Sol` (context 1M, reasoning Max, fast OFF, read-only, fresh context)
- Review date: 2026-08-27
- Final governed outcome: **REJECT**
- Recorded by: controller (verbatim findings from the reviewer's handoff)

## Verified artifact identities

- `BOOTSTRAP_PLAN.md`: `ab9a9020f91bd36bf5bb49504f754089835703d96b92f4a635b27fa9728b9bc9`
- `ROADMAP.md`: `cc81d063948a5588cc0f1041396aa218057b3e0474e3b9ec45f5d5a5fd849c1b`
- `TASK-001_PLAN.md`: `556a08a22ee128b13e5a5d95728f556734f3d8c30f0acc94f57271d978435c14`
- `REQUIREMENTS_TRACEABILITY.json`: `6e0a50bb37dfb80d4b1416c88692af1b8504e939bf377f5bb6a2b168d3821da1`
- `AUTHORITY_MANIFEST.json`: `45aef831bde59810034dccbc038879e377aff07d055fde4c1d9f1b22e3d7d56d`
- `REMEDIATION-1_ADJUDICATION.md`: `e54f99a04ea5c8b35215f650e5710e2cc70312500590fc5d3cdf78ded4727a8e`
- `DOCUMENT_READ_ORDER.md`: `44a2ced2c5e13b955be91ee893e54bd25bbea725f992e9c2d649ec4227a160b3`
- `PROJECT_MAP.md`: `3c0efc585f20d96b51d5b01541383ca37691fd0a2648e51dabf2dd020881f266`
- AMENDMENT-001: `3ea00519a4e7b79adb2e1f60afcfd4c393906033c148fd254fb1d71e15c61589`

Branch remained clean, at the exact commit, with unchanged hashes through final verification.

## Authority inspected (per reviewer)

All required control-plane governance, frozen baseline, role definition, and `BUILD_STATE.yaml`; canonical project `docs/README.md` and numbered documents `00`–`33`, with direct emphasis on docs 03, 07, 14, 16, 18, 22–25, and 28–30; all eight plan artifacts and attempt-1 review evidence.

## Findings

### FATH-P2-001 — BLOCKER
- Affected: `BOOTSTRAP_PLAN.md` §§3, 7.4; `TASK-001_PLAN.md` §§4.6–4.7, A4/A6; FA-OPEN-021.
- Basis: docs 03, 04, 21, 24, 29, 30; Oracle Policy §§4–7, 41.
- Observed: V2 creates `source_registry.id TEXT PRIMARY KEY`, while its Pydantic model exposes `source_id: str`. Canonical downstream contracts still reference `source_registry.source_id` as UUID. Doc 29 instead references a different parent shape, `sources(id)`. The plan neither defines a mapping nor propagates the type/column change across dependent contracts.
- Required condition: establish one coherent source-identity model, propagate compatible table, column, model, and FK types, classify the choice accurately, and provide an independent expected-schema oracle.

### FATH-P2-002 — HIGH
- Affected: `TASK-001_PLAN.md` §5, A1–A11, completion conditions.
- Basis: docs 03, 29, 30; Oracle Policy §§5, 11, 37.
- Observed: Seed data is textually descoped, but no acceptance criterion verifies that migrations leave `source_registry` empty or that no seed YAML/loader is introduced. All A1–A11 can pass with invented seed rows; A5 may even permit `sources_seed.yaml` because doc 16 lists it.
- Required condition: add candidate-bound negative verification for zero seed rows, no seed content/loader, and strictly synthetic non-persistent fixtures.

### FATH-P2-003 — HIGH
- Affected: `TASK-001_PLAN.md` §4.1 and A5.
- Basis: doc 16; doc 23 anti-drift rule; Oracle Policy §§5, 37.
- Observed: A5 calls for an "exact" comparison with doc 16, but TASK-001 defers portions of that tree, adds disclosed root paths and package initializers, and creates only a subset of canonical files. Full equality would fail; subset checking would not prove the required scaffold exists.
- Required condition: define a task-specific expected-tree oracle identifying required, permitted, deferred, and prohibited paths.

### FATH-P2-004 — BLOCKER
- Affected: `BOOTSTRAP_PLAN.md` §§9, 11; `TASK-001_PLAN.md` §11; roadmap governance.
- Basis: Constitution §§9, 19; Review Policy §§36–46; `BUILD_STATE.yaml`.
- Observed: CI is now correctly labelled SHA-bound evidence, but the plan states that until trusted verification exists, "merge eligibility rests on independent review + controller process." It also calls `main` protected while branch protection is unverified. Current state records trusted gates and receipts as `NOT_CONFIGURED` and merge eligibility as `NOT_ELIGIBLE`.
- Required condition: remove the model/controller merge bypass and sequence trusted exact-identity verification and repository protection before any candidate — including TASK-001 — is declared merge-eligible.

## TASK-001 oracle assessment

- A1–A3: `VALID` · A4: `CONFLICTING` · A5: `PARTIAL` · A6: `CONFLICTING` through FA-OPEN-021 · A7–A9: `VALID` for their stated, limited claims · A10: `VALID` only as SHA-bound test evidence, never as trusted acceptance · A11: `VALID` · No-seed scope boundary: `MISSING`

## Attempt-1 finding disposition

- PR-001: `NOT RESOLVED` · PR-002: `NOT RESOLVED` · PR-003: `RESOLVED` · PR-004: `RESOLVED` · PR-005: `RESOLVED` · PR-006: `NEWLY DEFECTIVE` (labelling fixed, merge bypass introduced) · PR-007: `RESOLVED`

FA-OPEN-020 remains governed rather than dropped; its dependency gate propagates through TASK-006 to TASK-007/008, TASK-011 through dependencies 003–010, and TASK-014 through "all above."

## FA-OPEN-021 adjudication

`NOT CONFIRMED`. Textual slugs are strongly supported as public source identifiers by docs 24, 29, and 30. They do not logically force V2's specific TEXT-only `source_registry.id` primary-key design or prove that all UUID source-reference contracts are superseded. The current classification as `DERIVED` is therefore unsupported.

## Reviewer self-audit

Read-only maintained, exact plan identity reviewed, no remediation performed, findings source-grounded. This review is evidence, not the formal trusted gate.
