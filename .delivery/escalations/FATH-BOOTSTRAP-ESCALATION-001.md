# FATH-BOOTSTRAP-ESCALATION-001 — BLOCKED_FOR_SALIM

**Date:** 2026-08-27
**Project:** FATH_AUTOPILOT (`baramiSG/Fath_Autopilot`)
**Task/scope:** FATH-BOOTSTRAP (bootstrap/architecture plan + roadmap + TASK-001 plan)
**Current state:** `BLOCKED_FOR_SALIM` — planning escalation ladder exhausted (Escalation Policy §12)
**Prepared by:** Salim Autonomous Project Controller (Claude Fable 5)

---

## Exact blocking question (minimum decision required)

> **Which source-identity model is authoritative for `source_registry` and every contract that references a source?**

The canonical corpus contradicts itself, and doc 23's anti-drift rule reserves new schema elements to your approval, so no agent may decide this:

| Source | Exact text | Identity type |
|---|---|---|
| doc 03 line 74 | `source_id: UUID = Field(default_factory=uuid4)` | UUID |
| doc 03 line 122 | `source_id: UUID` (AccessDecision) | UUID |
| doc 04 "Foreign keys" | `raw_archive.source_id → source_registry.source_id` | UUID |
| doc 05 | `UntrustedBlob.source_id: UUID` | UUID |
| doc 07 lines 107, 268 | `source_id: UUID` (Python UI props) | UUID |
| doc 21 DDL (twice) | `source_id UUID NOT NULL REFERENCES source_registry(source_id)` | UUID |
| doc 24 §1 | Week-1 sets use `qatar_open_data`, `world_bank`, `gdelt` | textual |
| doc 29 line 56 | `source_id: str` (onboarding checklist) | TEXT |
| doc 29 line 82 | `source_id TEXT PRIMARY KEY REFERENCES sources(id)` — table name `sources` does not even match doc 03's `source_registry` | TEXT |
| doc 29 line 223 | `source_id TEXT NOT NULL REFERENCES sources(id)` | TEXT |
| doc 30 | seed catalog uses textual ids | textual |

## Decision options

**Option A — Dual identifier (planner's proposal; controller recommends):**
- `source_registry.source_id UUID PRIMARY KEY` — satisfies docs 03/04/05/07/21 verbatim.
- `source_registry.slug TEXT NOT NULL UNIQUE` — carries the human-readable id (`qatar_open_data`, …) used by docs 24/29/30.
- Doc-29 compliance tables' FKs retarget to `source_registry(slug)` (their current DDL references a nonexistent `sources(id)` table, so remapping is unavoidable under every option).
- Every surface mapped explicitly: internal DB FKs + Python models = UUID; YAML definitions, compliance tables, human-facing references = slug; each event/UI payload field mapped one-by-one (doc 07 Python `source_id: UUID` stays UUID).
- The independent reviewer judged this design "technically possible" but requiring your authority because no canonical document defines `slug`.

**Option B — UUID-only:** doc 29/30 textual references would be rewritten as UUIDs. Contradicts their plain text; makes compliance tables and seed catalogs human-hostile.

**Option C — TEXT-only:** contradicts docs 03/04/05/07/21 verbatim UUID declarations (this was tried in plan V2 and rejected by the reviewer for exactly that reason).

**Your decision (choose one, or specify another):** A / B / C / other.

If you approve Option A (or a variant), it will be recorded as human-approved authority (AMENDMENT-002), the planning scope genuinely changes, and per Escalation Policy §6 a fresh planning cycle (plan V4, new 3-attempt review sequence) is justified. The planner will also correct the four remaining non-decision findings (P3-002…P3-005: oracle tightening for runtime versions/defaults/boundaries/dependency contract, seed-detection strengthening, tree-oracle scan domain, `.delivery` evidence boundary) — none of those require your input.

---

## Attempts performed (all evidence committed on `plan/bootstrap-and-task-001`)

| Attempt | Plan | Commit | Reviewer outcome | Evidence |
|---|---|---|---|---|
| 1 | V1 | `3735813` | REJECT — 7 findings (1 BLOCKER: seed authority gaps) | `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-1.md` (697adb4) |
| 2 | V2 | `77b0824` | REJECT — 4 findings (2 BLOCKERs: identity incoherence; merge bypass) | `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-2.md` (4aef325) |
| 3 (final) | V3 | `ca72280` | REJECT — 5 findings (1 BLOCKER: identity model requires human authority) | `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-3.md` |

- Model/reviewer sequence: Planner = Claude Fable 5 (thinking max); Reviewer = GPT-5.6 Sol (1M, max, fast OFF, fresh read-only context each attempt).
- Counters: `plan_review_attempt = 3/3` (exhausted); remediations 1 and 2 adjudication records committed alongside the plans.
- Progress across attempts was real: of 11 total distinct findings, 7 were resolved and stayed resolved (layout, A8/A9 scan oracles, Week-1 LLM posture, PG image classification, CI labeling, Entra/ADR handling, merge-bypass removal). What survived every round is the one genuine authority contradiction above.

## Why autonomy is exhausted

Escalation Policy §§8, 12: maximum 3 independent Sol plan-review attempts per unchanged planning scope; attempt 3 was rejected; the controller may not ask a fourth time, switch reviewers, weaken criteria, or start implementation on an unapproved plan. The decisive blocker (FATH-P3-001) explicitly requires a human-approved decision, which no agent may fabricate.

## Also pending for later (does NOT need a decision now)

- **FA-OPEN-020:** the 16-source seed value table (base URLs, reliability tiers, rate limits) + Tier-0 onboarding checklists — needed before TASK-006 (seeding), not before TASK-001.
- **GATE-SETUP:** branch protection + trusted exact-identity verification on `baramiSG/Fath_Autopilot` — required before any merge becomes eligible; the plan sequences it and it needs your repository-admin authorization when reached.

## Earliest safe resume state

Upon your explicit decision: controller records it as AMENDMENT-002 (or your wording), planner regenerates plan V4 under the clarified authority (also fixing P3-002…005), and a fresh independent review sequence begins. No history is erased; all three rejected plans and reviews remain in the record.
