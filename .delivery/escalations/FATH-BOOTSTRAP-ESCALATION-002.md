# FATH-BOOTSTRAP-ESCALATION-002 — BLOCKED_FOR_SALIM

**Date:** 2026-08-27
**Project:** FATH_AUTOPILOT (`baramiSG/Fath_Autopilot`, PR #1)
**Task/scope:** FATH-BOOTSTRAP (bootstrap/architecture plan + roadmap + TASK-001 plan)
**Current state:** `BLOCKED_FOR_SALIM` — review sequence 2 ladder exhausted (Escalation Policy §§8, 12)
**Prepared by:** Salim Autonomous Project Controller (Claude Fable 5)

---

## Why this escalation exists

Plan V6 received the third and final REJECT of review sequence 2. Governance permits no fourth autonomous review attempt for this scope. Unlike ESCALATION-001, no project authority is missing — the plan is nearly review-clean (AMENDMENT-002 conformance: full PASS for the first time; 15 of 16 acceptance-criterion oracles VALID; all regression checks pass). What remains are three narrow findings, and the autonomous ladder ran out before they could be fixed.

## The three remaining findings (full text: `.delivery/reviews/FATH-BOOTSTRAP/plan-review-seq2-attempt-3.md`)

1. **FATH-V6-001 HIGH** — the migration zero-DML detector catches all direct forms (including the previously cited `op.execute(sa.insert(...))`) but can still be evaded by dynamic indirection: `getattr(op, "execute")(getattr(sa, "insert")(table).values(...))`, aliased imports, or f-string SQL assembled from separate literals. Fix: prohibit dynamic attribute/call indirection and alias forms in migrations (mechanically checkable — e.g., ban `getattr`/`eval`/`exec`/aliased `op`/`sa` imports in migration files outright), plus negative fixtures for these variants.
2. **FATH-V6-002 MEDIUM** — AGE and pgvector are pinned by git release tags, which are mutable. Fix: pin to immutable commit SHAs or checksum-verified archives (or explicitly narrow the reproducibility claim).
3. **FATH-V6-003 LOW** — stale cross-references ("v5") in two plan files; a stale "15 constraints" figure in the control-plane state summary (the controller has already corrected the state metadata side).

## Progress evidence across the ladder (nothing was wasted)

| Round | Plan | Findings | Trend |
|---|---|---|---|
| Seq1 attempts 1–3 | V1–V3 | 7 → 4 → 5 | ended in ESCALATION-001 → resolved by your AMENDMENT-002 |
| Seq2 attempt 1 | V4 | 9 (deeper standard applied to amended scope) | 7 of 9 resolved next round |
| Seq2 attempt 2 | V5 | 5 | 4 of 5 resolved next round |
| Seq2 attempt 3 | V6 | 3 (1 HIGH, 1 MEDIUM, 1 LOW) | AMENDMENT-002 PASS; A13 is the only non-VALID oracle |

Model/reviewer sequence unchanged throughout: planner = Claude Fable 5 (inherited Max runtime after the correction); reviewer = fresh read-only GPT-5.6 Sol per attempt. All plans, reviews, and adjudications are committed on `plan/bootstrap-and-task-001`; latest plan commit `d019b2e`.

## Minimum decision required from Salim (choose one)

**Option A — Authorize one additional scoped correction cycle (controller recommends).**
You authorize plan V7 strictly limited to correcting FATH-V6-001/002/003 (no other plan content may change), followed by a fresh independent Sol review sequence for the corrected plan. Your authorization is the human decision that opens a new governed sequence (Escalation Policy §6). Expected cycle cost: one planner correction + one review.

**Option B — Accept narrowed claims and proceed.**
You explicitly accept: (1) the zero-DML oracle covers direct API forms only, with dynamic-indirection risk mitigated by A12's observed zero-row states and by independent implementation review rather than by the mechanical scanner; (2) AGE/pgvector remain tag-pinned with resolved digests recorded as candidate evidence. The claims in the plan are narrowed accordingly (an authorized oracle-scope decision, not a weakening by an agent), V6-003's references are fixed, and the plan proceeds to implementation on that basis.

**Option C — Any other explicit direction.**

## Also pending (unchanged, not blocking this decision)

- FA-OPEN-020 — seed value table + Tier-0 onboarding checklists (gates TASK-006).
- GATE-SETUP — branch protection + trusted verification on the target repo (gates any merge; needs your repository-admin authorization when reached).

## Earliest safe resume state

On Option A: planner produces V7 (scoped), fresh Sol review sequence begins. On Option B: controller records your acceptance as an authority note, planner applies the narrowed wording + V6-003 fixes as a bounded edit, one fresh Sol review validates the recorded scope, then implementation dispatch. Either way, no history is rewritten and PR #1 stays Draft.
