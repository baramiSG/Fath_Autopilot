# FATH-BOOTSTRAP — Remediation 2: Diagnosis and Adjudication of Plan-Review Attempt-2 Findings

**Project:** FATH_AUTOPILOT · **Scope:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT / TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max)
**Findings record adjudicated:** `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-2.md` (commit `4aef325`, REJECT, 4 findings) against plan commit `77b08242d624bbb4bbe4f91553209cdee201fb48`.
**Outcome:** all four findings adjudicated **VALID**; corrections produce plan V3 — review attempt **3 of 3, the final autonomous attempt**.

---

## Root-cause diagnosis (Escalation Policy §11 — why two independent reviews failed)

I verified the controller's observation against both rejection records and my own remediation conduct, and **confirm it**. The recurring root cause across V1 and V2 is one defect class: **claims and designs scoped wider than what the cited authority plus the actual runtime state support.**

Concrete instances:

1. **V1:** asserted a complete 16-record seed oracle when authority establishes identities but not values (PR-001); called candidate-controlled CI "trusted verification" while nothing was configured (PR-006); claimed doc-16 conformance while deviating (PR-002).
2. **V2, mechanism of failure:** I remediated *finding-by-finding at the text that was flagged*, instead of re-deriving each affected design from the full corpus and mechanically simulating each oracle:
   - For the identifier model I re-read only the three documents the finding cited (03/29/30) and chose a TEXT-only PK — without sweeping the corpus for every identity-bearing contract. Docs 04 and 21 carry literal UUID FK DDL against `source_registry(source_id)`; the choice broke them unexamined (P2-001).
   - I wrote "exact" doc-16 comparison language without executing the oracle mentally against the planned candidate tree, where it visibly fails (deferred files, added initializers) (P2-003).
   - I stated a seed descope without an enforcing negative check, leaving the boundary unverifiable (P2-002).
   - I wrote a merge-eligibility sentence ("independent review + controller process") that contradicted the constitution's fail-closed rule and BUILD_STATE's `NOT_ELIGIBLE`/`NOT_CONFIGURED`/`NOT_VERIFIED` truth, and called `main` protected without evidence (P2-004).

**V3 correction posture (applied throughout):** conservative precision — (a) every consequential schema/design element carries an explicit citation and a classification no stronger than its citation supports; (b) every acceptance criterion was mentally executed against the planned candidate before being written, and each has a mechanical, non-circular check; (c) every gate/merge statement was checked verbatim against BUILD_STATE; (d) the whole artifact set was swept for the same defect classes (duplicated stale rows from remediation 1 were found in BOOTSTRAP_PLAN §3 and removed; FA-REQ-CP-001/CP-003/W1-018 wording tightened).

## Adjudication

### FATH-P2-001 — BLOCKER — **VALID**

**Re-verified full identity landscape:** UUID storage contracts: doc 03 `source_id: UUID = Field(default_factory=uuid4)` + `AccessDecision.source_id: UUID`; doc 04 record `source_id: UUID` + "Foreign keys": `raw_archive.source_id → source_registry.source_id`; doc 21 DDL twice: `source_id UUID NOT NULL REFERENCES source_registry(source_id)`; doc 05 `UntrustedBlob.source_id: UUID`. Textual contracts: doc 24 §1 Week-1 sets; doc 24 §§4–5/§8 payloads `source_id: str` paired with `source_name: str`; doc 29 `source_id TEXT` compliance tables referencing `sources(id)`; doc 30 template; doc 06 payloads `source_id: str`. V2's TEXT-only PK indeed broke the UUID contracts, and the reviewer's non-confirmation of FA-OPEN-021 was correct.

**Correction — dual-identifier model (BOOTSTRAP_PLAN §7.4), nothing superseded:** `source_registry.source_id UUID PRIMARY KEY` (SPECIFIED — docs 03/04/21 verbatim) + `slug TEXT NOT NULL UNIQUE` (textual identifier existence SPECIFIED by usage in docs 24/29/30/06; distinct-column housing DERIVED — one field cannot be two types; column name PROPOSED). Full propagation map recorded and binding on future task plans: UUID FKs verbatim; doc-29 TEXT columns verbatim FK → `source_registry(slug)`; event/UI `source_id: str` carries the slug; doc-30 YAML key maps to slug at seed load; `SourceRegistryRecord` = doc-03 verbatim + `slug` + doc-24 `status` (the corpus's own amendment pattern). Independent expected-schema oracle added (TASK-001 A4): hand-derived, per-element-cited `expected_schema.json` fixture compared mechanically against `information_schema` — not generated from the implementation models. Fallback recorded: if the reviewer finds the `slug` addition indefensible, the minimal Salim question is stated verbatim in §7.4.

### FATH-P2-002 — HIGH — **VALID**

The descope was textual only; nothing verified it. **Correction:** new mechanical criteria — **A12** (zero rows in `source_registry` after fresh `upgrade head` AND after the downgrade/upgrade cycle, run independent of tests) and **A13** (no `sources_seed.yaml`, no `*seed*` path under `src/` via `git ls-files`; synthetic-marker scan on fixtures); `sources_seed.yaml` placed in A5's PROHIBITED set for this candidate (it is TASK-006 scope despite appearing in doc 16); fixture non-persistence defined (rollback/ephemeral DB, zero-row checks on fresh schema). CI step order fixed accordingly (TASK-001 §4.8).

### FATH-P2-003 — HIGH — **VALID**

"Exact" comparison was infeasible: TASK-001 defers canonical files and adds disclosed paths, so equality fails and subset-checking proves nothing. **Correction:** A5 rebuilt as a four-set expected-tree oracle (TASK-001 §6.1) with enumerated **REQUIRED / PERMITTED / DEFERRED / PROHIBITED** sets, each entry bound to doc 16 or the disclosed-additions list, committed as a hand-derived manifest and checked mechanically (required-exist; prohibited-absent; everything-present ∈ required ∪ permitted).

### FATH-P2-004 — BLOCKER — **VALID**

The V2 sentence "merge eligibility rests on independent review + controller process" was a bypass of constitution §§9/19 and review policy §§36–46, and "`main`: protected target branch" claimed unverified protection (BUILD_STATE: `branch_protection: NOT_VERIFIED`). **Correction:** bypass removed everywhere; BOOTSTRAP_PLAN §9 now defines **GATE-SETUP** as a sequenced, verified precondition to ANY merge eligibility: (1) branch protection configured by Salim and proven ACTIVE via mechanical GitHub API evidence recorded under `.delivery/evidence/GATE-SETUP/`; (2) trusted exact-identity verification with recorded receipts per review policy §§36–46; (3) BUILD_STATE updated from that evidence. Until all three verify, every candidate — TASK-001 included — halts at **REVIEW_APPROVED** and is **NOT merge-eligible**. Implementation and review may proceed in parallel; merging may not. No control weakened — the change forbids merges the prior wording permitted. Language aligned in TASK-001 §11, ROADMAP governance, traceability FA-REQ-CP-001/CP-003, and the branch-model bullet.

---

## Artifacts changed in V3

| Artifact | Change |
|---|---|
| TASK-001_PLAN.md | Rewritten v3: dual-identity schema (§4.6–4.7), A4 independent expected-schema oracle, A5 four-set tree oracle (§6.1), new A12/A13 negative criteria, §5 enforced seed boundary, §11 gate sequencing, CI step order |
| BOOTSTRAP_PLAN.md | v3: §3 rows corrected + stale duplicates removed, §4.2/4.3 rows, §7.4 rewritten (dual identity + propagation map + fallback question), §9 GATE-SETUP sequencing replacing the bypass, §11 protection claim corrected, §12/§14 updated |
| ROADMAP.md | Governance section: GATE-SETUP required before any merge; open-items list updated (FA-OPEN-021 wording; GATE-SETUP item) |
| REQUIREMENTS_TRACEABILITY.json | FA-REQ-W1-001 identity wording; FA-REQ-CP-001 gate sequencing; FA-REQ-CP-003 REVIEW_APPROVED halt; FA-REQ-W1-018 oracle wording; FA-OPEN-021 rewritten (dual identity + propagation + fallback) |
| AUTHORITY_MANIFEST.json, DOCUMENT_READ_ORDER.md, PROJECT_MAP.md | Unchanged (swept; no identity/gate/oracle over-claims found) |

## Open items and Salim questions

- No new OPEN item. FA-OPEN-021 remains open pending reviewer confirmation of the dual-identifier reconciliation, now with a pre-formulated minimal Salim fallback question. GATE-SETUP (Salim) was already a roadmap item and is now explicitly sequenced BEFORE first merge.
- FA-OPEN-020 unchanged (gates TASK-006+).

This record is planning material, not project authority; it approves nothing. A rejection of attempt 3 escalates to `BLOCKED_FOR_SALIM` — no attempt 4 will be created.
