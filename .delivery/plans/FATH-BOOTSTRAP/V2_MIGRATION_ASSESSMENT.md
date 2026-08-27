# FATH-BOOTSTRAP — V1 → V2 Policy Migration Assessment (one-time)

**Assessment ID:** FATH-BOOTSTRAP-V2-MIGRATION-001
**Date:** 2026-08-27
**Project:** FATH_AUTOPILOT (`baramiSG/Fath_Autopilot`, PR #1)
**Subject plan:** FATH-BOOTSTRAP-PLAN-V6 — commit `d019b2e81a2561bfea72d58620e2fefadbefbb14` (artifact SHA-256 identities recorded in control-plane BUILD_STATE; unchanged and re-verified for this assessment)
**Prepared by:** Salim Autonomous Project Controller / V2 Orchestrator (Claude Fable 5 Thinking Max)
**Assessment outcome:** **APPROVED_BY_V2_MIGRATION** — no genuine B1–B7 plan blocker remains; all unresolved findings transfer to `TASK-001-IAC.md`

---

## 1. Authority for this migration

1. **Owner directive (Salim, 2026-08-27):** explicit instruction "RECOVER FATH UNDER AUTONOMOUS DELIVERY V2" — a one-time V1 → V2 policy migration for `FATH-BOOTSTRAP-PLAN-V6`. Operative constraints, verbatim in substance:
   - do not create PLAN V7; do not restart the three-attempt V1 planning ladder;
   - do not discard V1–V6 history, AMENDMENT-001, AMENDMENT-002, reviews, evidence, or PR #1;
   - perform one migration assessment of the existing V6 plan using ONLY the V2 B1–B7 plan-blocker taxonomy;
   - classify every unresolved V4/V5/V6 finding as BLOCKER only if genuinely B1–B7, otherwise as an IMPLEMENTATION OBLIGATION transferred into TASK-001-IAC;
   - do not reject V6 for implementation mechanics that belong in implementation, deterministic verification, tests or CI;
   - if no genuine B1–B7 blocker remains: mark V6 `APPROVED_BY_V2_MIGRATION`, preserve legacy history, dispatch Cursor Grok 4.6 XHigh into TASK-001 implementation (TDD-first where practical, satisfy the IAC, stop UNCOMMITTED for independent GPT-5.6 Sol implementation review);
   - keep Draft PR #1 as the historical lifecycle PR; create no additional PR for this recovered task.
2. **`governance/AUTONOMOUS_DELIVERY_V2_RATIFICATION.md`** (control plane, HUMAN_RATIFIED, effective 2026-08-27): V2 governs autonomous delivery; V1 operational provisions conflicting with V2 are superseded; V1 records remain historical.
3. **`governance/AUTONOMOUS_DELIVERY_POLICY_V2.md`** §10 (closed B1–B7 blocker list; automatic obligation transfer; mandatory classification), §15 (CI owns mechanical truth; a not-fully-designed future mechanical checker is an IAC obligation, never a plan rejection), §10.4 ("no unresolved B1–B7 → plan is APPROVED; all remaining findings transfer to the IAC").
4. **`.cursor/rules/severity-taxonomy.mdc`** §2: severity alone may never cause plan rejection; migration-scanner mechanics, dependency/image binding mechanics, validator mechanics and editorial defects transfer to the IAC unless they expose a genuine B1–B7 defect.

**ESCALATION-002 disposition:** `FATH-BOOTSTRAP-ESCALATION-002.md` offered Options A (authorize plan V7), B (accept narrowed claims), or C (any other explicit direction). The owner directive is an explicit **Option C**: a governed policy migration. ESCALATION-002 is therefore **RESOLVED_BY_OWNER_DIRECTIVE (V2 migration)**. No escalation content is rewritten.

## 2. What this assessment is — and is not

- It **is** a one-time reclassification of the already-recorded independent review findings against the V2 closed plan-blocker taxonomy, performed by the Orchestrator under explicit owner direction.
- It is **not** a new plan revision (plan V6 artifacts remain byte-identical; every recorded SHA-256 stands), **not** a seventh review attempt, and **not** a substitute quality review. The plan-quality evidence remains the six independent GPT-5.6 Sol reviews (V1–V6), all preserved.
- **Independence note (recorded deliberately):** the V6 plan was authored by the Fable planner seat and this assessment is performed by the Fable Orchestrator seat. This is lawful here because (a) the owner directive explicitly assigns the migration assessment to the V2 controller; (b) the assessment applies a closed taxonomy to findings produced by the independent Sol reviewer — it introduces no new self-judged quality claims; (c) every conformance fact relied on below is the independent reviewer's own recorded result, not the controller's opinion of its own work; and (d) the deliberately exacting V2 gate — independent Sol review of the actual implementation, including every transferred obligation — remains fully in force. No self-certification of implementation occurs anywhere in this flow.

## 3. Unresolved finding inventory (completeness traced)

Lineage across review sequence 2 (evidence: `plan-review-seq2-attempt-1.md`, `plan-review-seq2-attempt-2.md`, `plan-review-seq2-attempt-3.md`):

- V4 findings (9): V4-001, V4-004..009 RESOLVED (per V5/V6 reviews); V4-002 residue became V5-002 (RESOLVED in V6); V4-003 residue became V5-001.
- V5 findings (5): V5-002 RESOLVED; V5-003 RESOLVED; V5-001 residue → **FATH-V6-001**; V5-004 residue (Redis resolved; AGE/pgvector same-class gap) → **FATH-V6-002**; V5-005 residue (schema count resolved; stale metadata/references) → **FATH-V6-003**.
- V6 review regression section: "All previously resolved findings preserved" (enumerated); AMENDMENT-002 conformance **PASS**; TASK-001 oracles A1–A12, A14–A16 **VALID**, A13 **PARTIAL**; "TASK-001 remains coherently bounded and generally implementable."

**The complete unresolved set from the V4/V5/V6 history is exactly: FATH-V6-001, FATH-V6-002, FATH-V6-003.** No other finding from any review round remains open.

## 4. V2 classification of each unresolved finding (Policy V2 §10.3 format)

### FINDING-1 (legacy FATH-V6-001)

```text
FINDING-1
claim: The A13b-ii AST-allowlist migration DML detector catches all direct DML
       forms but is evadable by dynamic indirection (getattr(op,"execute")(...)),
       aliased imports of op/sa, and DML keywords split across separate string
       literals (indirect f-string assembly). The six committed negative fixtures
       prove the six named specimens only, not the broader zero-DML claim.
severity: HIGH
classification: OBLIGATION
basis: Policy V2 §10.2 (obligation examples include "migration negative fixtures"
       and "a missing mechanical CI check"); §15 ("At plan review, the Reviewer
       must not reject because a future mechanical checker is not fully designed.
       The missing checker becomes an IAC obligation."); severity-taxonomy §2
       ("migration-scanner mechanics ... must transfer to the Implementation
       Acceptance Checklist unless they expose a genuine B1-B7 defect");
       owner directive ("Do not reject V6 for implementation mechanics that
       belong in implementation, deterministic verification, tests or CI").
if OBLIGATION, why not plan-level:
       Tested against each B: not B1 (no missing/contradictory authority — the
       zero-DML invariant is authoritatively fixed and undisputed); not B2/B3
       (objective and scope confirmed by the final review); not B4 (the
       architecture embraces the invariant; the finding concerns checker
       completeness, not the direction); not B5 (the data-boundary control
       exists — layered A12 three-point zero-row observation, A13a/c/d scans,
       detector, and independent diff review; the finding hardens one mechanical
       layer of an existing control rather than exposing a missing control);
       not B6 (no schema/API/contract decision involved); not B7 (acceptance
       criteria are present, falsifiable and viable — the final review itself
       grades A13 PARTIAL, not absent/unfalsifiable, confirms A12 VALID, and
       ESCALATION-002 records the fix as "mechanically checkable". The V1
       reviewer's BLOCKER-B7 label was assigned under the V1 oracle-completeness
       standard, which V2 supersedes for checker mechanics). The reviewer's
       required condition is preserved at full strength as IAC-001 and is
       enforceable against the actual detector code with proving negative
       fixtures — precisely the artifact-gated verification V2 mandates.
```

### FINDING-2 (legacy FATH-V6-002)

```text
FINDING-2
claim: AGE and pgvector are pinned by git release tags, which are mutable;
       identical candidate content can retrieve different extension source.
       Redis, GitHub Actions and gitleaks are already immutably bound.
severity: MEDIUM
classification: OBLIGATION
basis: Policy V2 §10.2 (obligation examples include "image digest resolution"
       and "dependency version parsing"); §15 (CI owns "dependency resolution
       and version checks; image digests"); severity-taxonomy §2 ("image digest
       resolution" listed as implementation mechanics).
if OBLIGATION, why not plan-level:
       The plan's direction — full supply-chain pinning discipline — is already
       adopted and mostly bound (digest-pinned Postgres base and Redis,
       SHA-pinned actions, checksum-verified gitleaks). The residue is the
       binding FORM for two source-built extensions, a deterministic
       implementation mechanic verifiable byte-exactly in the actual Dockerfile
       at the implementation gate. Not B1-B7: no authority gap, no scope or
       objective defect, no unsafe architecture, no missing control class
       (the pinning control exists; its strongest binding form is the
       obligation), no irreversible contract, no untestability.
       Preserved at full strength as IAC-002.
```

### FINDING-3 (legacy FATH-V6-003)

```text
FINDING-3
claim: Stale cross-references: TASK-001_PLAN.md §2 authority table cites
       "BOOTSTRAP_PLAN.md (v5)" (line 33) and BOOTSTRAP_PLAN.md cites
       "TASK-001_PLAN.md v5" (line 129), both actually v6; control-plane
       BUILD_STATE.yaml carried a stale "15 constraints" figure in its V5
       history summary.
severity: LOW
classification: OBLIGATION
basis: Policy V2 §10.2 (obligation examples include "documentation count
       errors"); severity-taxonomy §2 (LOW/editorial items never block absent
       an explicit acceptance requirement).
if OBLIGATION, why not plan-level:
       Purely editorial metadata. The operative artifacts are identified by
       SHA-256 in control-plane state, so no ambiguity about which content is
       authoritative exists. Correcting the labels inside the plan files would
       change their hashes and manufacture a new plan identity — exactly what
       the owner directive prohibits ("Do not create PLAN V7"). Handled by the
       §6 errata below plus the durable-state correction; residual reviewer
       verification recorded as IAC-003.
```

## 5. B1–B7 sweep of plan V6 as a whole

Beyond the three findings, the closed list was swept against the plan and the final independent review's own recorded results:

| ID | Blocker class | Result | Evidence |
|---|---|---|---|
| B1 | Missing/contradictory material authority | NONE | Source-identity contradiction resolved by human-approved AMENDMENT-002 (docs/34); final review records AMENDMENT-002 conformance **PASS** (§§1–13). AMENDMENT-001 applied. FA-OPEN-020 gates TASK-006, not TASK-001 (plan §8). |
| B2 | Wrong objective | NONE | Final review: plan implements the selected bounded task (repository foundation / registry schema); "coherently bounded and generally implementable". |
| B3 | Material scope violation | NONE | Boundedness confirmed by final review; A16 diff-boundary and A5 tree oracle bind the scope mechanically. |
| B4 | Unsafe architecture / explicit-invariant violation | NONE | Architecture per docs/02/16/22/28 as amended; no review round V1–V6 recorded an unsafe-architecture finding against V6 content; zero-DML/zero-seed invariants are embraced and enforced in layers. |
| B5 | Missing security/tenancy/secrets/privacy/data-boundary control | NONE | Data classification PUBLIC/OWNER-AUTHORED (§3a); secrets controls (A9 checksum-pinned gitleaks, .env rules); seed/data boundary (A12 three-point zero-row + A13a–d); no tenancy in scope for this slice. FINDING-1/2 harden existing controls' mechanics — no control class is absent. |
| B6 | Irreversible schema/API/contract decision without authority | NONE | Schema per human-approved AMENDMENT-002 + docs/03/24; PROPOSED mechanisms (uuid default, trigger mechanism, bigint headroom) disclosed as PROPOSED with full downgrade required (A3); nothing irreversible is decided without authority. |
| B7 | Untestable task | NONE | 16 acceptance criteria with oracles; final review grades 15 of 16 fully VALID, A13 PARTIAL (checker mechanics → IAC-001); A12 VALID. Criteria are present, falsifiable, viable. |

**Verdict:** No genuine B1–B7 blocker exists in plan V6. Per Policy V2 §10.4 and the owner directive:

> **FATH-BOOTSTRAP-PLAN-V6 (commit `d019b2e`, artifact hashes unchanged) is APPROVED_BY_V2_MIGRATION.**
> All remaining findings transfer to `TASK-001-IAC.md`. The V1 planning ladder for this scope is closed. No plan V7 exists or may be created for this scope.

## 6. Errata (discharges the editorial substance of FINDING-3 without touching V6 identity)

1. `TASK-001_PLAN.md` line 33, "`BOOTSTRAP_PLAN.md (v5)` §§4, 6, 7.4, 9, 10.6, 12" — **read as `BOOTSTRAP_PLAN.md (v6)`**. The cited section numbers are correct in v6.
2. `BOOTSTRAP_PLAN.md` line 129, "(`TASK-001_PLAN.md` v5)" — **read as `TASK-001_PLAN.md` v6**.
3. The authoritative constraint count for `source_registry` is **13** (6 enum CHECKs, 5 numeric CHECKs, PK, UNIQUE), as pre-bound in `TASK-001_PLAN.md` §6.0. Control-plane BUILD_STATE's V5-era summary text retains "15" solely as a historical record of what V5 claimed; the V6 record and this errata carry the correction. BUILD_STATE receives an explicit correction note with this migration.

The V6 plan files remain byte-identical; their recorded SHA-256 identities are unchanged. This errata note is the governed correction record.

## 7. Recovered lifecycle topology (owner-directed deviations from the default V2 sequence, recorded)

1. **Lifecycle PR:** Draft PR #1 (`plan/bootstrap-and-task-001` → `main`) remains the single canonical lifecycle PR for this recovered bounded delivery unit. The default V2 rule "PR is opened after implementation approval" is satisfied in substance — no *new* PR is created before approval; the pre-existing Draft PR is a preserved V1 historical artifact the owner explicitly retained.
2. **Working branch:** implementation occurs on `plan/bootstrap-and-task-001` (uncommitted until independent implementation APPROVE), because cutting `task/TASK-001-repository-foundation` from `main` would require a second PR, which the owner prohibited.
3. **Governed base identity (adapts TASK-001_PLAN §6.3 to the recovered topology, mechanism fully preserved):** the plan text assumed the plan baseline would be merged to `main` and the task branch cut from it. Under the recovery, the **governed base = the exact head commit of `plan/bootstrap-and-task-001` containing this migration record**, recorded (a) by the controller as `task_base_sha` in control-plane BUILD_STATE and (b) by the implementer in `.delivery/evidence/TASK-001/BASE_SHA.txt`. The A16 mechanism is unchanged: 40-hex ancestor assertion, `git diff --name-status --no-renames <BASE_SHA> HEAD`, docs/-untouched rule, `.delivery/` additions only under `.delivery/evidence/TASK-001/`, reviewer asserts BASE_SHA.txt == BUILD_STATE `task_base_sha`. The anti-tamper property (candidate cannot choose its own base) is preserved by the dual independent recording.
4. **Merge gates unchanged:** implementation APPROVE → commit exact approved candidate → push (updates PR #1) → CI green on the exact SHA → GATE-SETUP (branch protection + trusted verification, still NOT_CONFIGURED/NOT_VERIFIED) must be satisfied before any merge eligibility, per TASK-001_PLAN §11. Nothing in this migration weakens the merge gate.

## 8. Preservation statement

- Plans V1–V6, all six review records, all adjudication records, both escalations, AMENDMENT-001, AMENDMENT-002, RUNTIME_AUDIT_NOTE_001 and PR #1 are preserved unchanged.
- This assessment and `TASK-001-IAC.md` are additive artifacts committed by the controller before implementation dispatch; they are part of the governed base, not of the implementation candidate.

## 9. Next governed state

`IMPLEMENT` — dispatch `implementer` (Cursor Grok 4.6 XHigh) into TASK-001 IMPLEMENT mode against plan V6 + TASK-001-IAC; TDD-first where practical; stop UNCOMMITTED; then independent implementation review (`implementation-reviewer`, GPT-5.6 Sol, 1M, Max, fast OFF). Stop only for a genuine BLOCKED_FOR_SALIM condition under V2.
