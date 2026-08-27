# Fath Autopilot — Document Read Order

**Artifact type:** Navigation aid (NOT project authority)
**Project:** FATH_AUTOPILOT · **Task:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT (Claude Fable 5, 1M, Thinking ON, Max)
**Baseline commit:** `ae5a4ea7db30d9ba243e29c98424702f5e0fb7a1` · **Amendment commits:** `234a24d9e012710352d35aa5b1314a6395614945` (adds AMENDMENT-001, docs/33) · `af00923853e0234da403231258c822b949e9da00` (adds AMENDMENT-002, docs/34)

> **WARNING.** This file exists only to make agent re-orientation efficient. The canonical documents under `docs/` remain the sole project authority. Where this file summarizes, the summary has no authority. Always return to the canonical source for consequential decisions. Verify document integrity against `AUTHORITY_MANIFEST.json` hashes before relying on this order.

---

## 0. Always-read: delivery governance (control plane)

These live in the **control-plane repository** `baramiSG/salim-autonomous-build`, not in this repo. Every governed agent session reads them first.

1. `governance/AUTONOMOUS_DELIVERY_CONSTITUTION.md`
2. `governance/ROLE_AND_MODEL_POLICY.md`
3. `governance/ORACLE_POLICY.md`
4. `governance/REVIEW_AND_ACCEPTANCE_POLICY.md`
5. `governance/ESCALATION_POLICY.md`
6. `governance/GOVERNANCE_BASELINE.json`
7. `.delivery/state/BUILD_STATE.yaml` (current durable state)

The control plane defines **how** work is governed. The `docs/` corpus in this repo defines **what** must be built.

## 1. Project-wide canonical set (read for every implementation/review session, in this order)

| Order | Document | Why in this position |
|---|---|---|
| 1 | `docs/00_MASTER_BUILD_CONTEXT.md` | Entry document; product, restrictions, locked stack, five stores, first milestone. |
| 2 | `docs/33_AMENDMENT_001_COMPUTE_AND_LLM_PROVIDER.md` | **Top of project-document precedence (HUMAN_APPROVED_AMENDMENT, with docs/34) — wins over README, 00–32 incl. 24 where they conflict.** No A100s; RTX 5090 workstation compute target; no Azure OpenAI; frontier LLM APIs via provider-agnostic client; interpretation rules for every "GPT-5.4" mention. Read immediately after 00 so all later reading is amendment-corrected. |
| 3 | `docs/34_AMENDMENT_002_SOURCE_IDENTITY.md` | **Top of project-document precedence (HUMAN_APPROVED_AMENDMENT) — wins over EVERYTHING earlier, including 33 and 24, where conflicting (no conflict with 33; different domains).** Source identity: `source_registry` single canonical table; `source_id` UUID PK; `slug` TEXT NOT NULL UNIQUE; universal semantic rule; all persisted source FKs → `source_registry(source_id)`; doc-29 TEXT FK DDL superseded; YAML keys on `slug`; transport `source_id` = serialized UUID; §12 propagation sweep (see `PROPAGATION_MAP.md`); §13 TASK-001 schema oracle. Read immediately after 33 so every later source-identity mention is read correctly. |
| 4 | `docs/24_FINAL_IMPLEMENTATION_CORRECTIONS.md` | **Override layer for everything the amendments do not address — wins over docs 00–23 where they conflict.** Its §1 `sources`-table DDL, Week-1 textual sets, and payload `source_id: str` fields are read under docs/34 §§1/9/11. |
| 5 | `docs/README.md` | Documentation map, build constraints, v3 final reading rule. |
| 6 | `docs/02_ARCHITECTURE_DECISIONS.md` | Locked decisions + ADR supersession rule (reasoning-model row and "no extra frontier LLMs" clause amended by 33). |
| 7 | `docs/16_PROJECT_STRUCTURE_AND_MODULE_BOUNDARIES.md` | Canonical layout and module boundary rules. |
| 8 | `docs/17_BUILD_PLAN_AND_VERIFICATION.md` | Six-week plan and verification checklist. |
| 9 | `docs/23_IMPLEMENTATION_COVERAGE_CHECKLIST.md` | Readiness gates, Week-1 done criteria, anti-drift rule, final-build checks. |
| 10 | `docs/20_TERMINOLOGY.md` | Controlled vocabulary (fast read; prevents naming drift). |

## 2. Task-specific sets (load the sets matching the active task's domain)

| Domain | Canonical documents |
|---|---|
| LLM client / reasoning provider / compute sizing | `33` (AMENDMENT-001 — governing), `05` (prompt assembly), `14` (budgets), `02` (as amended) |
| Source identity (any surface touching a source id) | `34` (AMENDMENT-002 — governing), then the owning contract doc; per-surface mapping in `PROPAGATION_MAP.md` (aid) |
| Source registry / Access Guard / crawling | `34` (identity), `03`, `09`, `29` (DDL as superseded by 34 §7), `30` (YAML keys per 34 §8) |
| Memory stores / database schema | `04`, `22` (+ `24` §§2–3 corrections) |
| Trust boundary / sanitization / injection | `05` (+ `24` §7), `12` |
| Events / event bus | `06` (+ `24` §5) |
| Fath Canvas / UI | `07` (+ `24` §4), `25` (SSE filtering) |
| Agents and boundaries | `08` |
| Embeddings / retrieval / connections | `10`, `21` (+ known deltas recorded in traceability; + `33` for workstation GPU sizing) |
| Sanad validation | `11` (+ `24` §9), `27` |
| Source poisoning | `12` |
| Workflows / heartbeats / state | `13` |
| Budgets / rate limits | `14` (+ `24` §11; + `33` interpretation rule 4) |
| Audit / provenance | `15` (+ `24` §8) |
| Auth / RBAC / approvals | `25` (+ `24` §12; production provider flagged OPEN by `33`) |
| Simulation / policy tournament | `26` (+ `24` §10) |
| Evaluation / quality gates | `27` |
| Operations / backup / DR / migrations / secrets | `28` (Azure hosting options flagged OPEN by `33`; self-hosted paths operative interim) |
| Week-1 build tasks | `18` (+ everything `18` cites: `04`, `06`, `07`, `16`) |
| Week-2 build tasks | `31` (+ its build-context list: 00–16, 24, 27) |
| Production/demo readiness | `32` |
| Risk context (any task) | `19` |

## 3. Reference-only material

- `docs/Fath_Autopilot_Technical_Docs_Final_Combined.md` — convenience concatenation; **never cite it as authority**; it may lag the canonical numbered files.

## 4. Navigation aids (NOT authority)

- `.delivery/plans/FATH-BOOTSTRAP/AUTHORITY_MANIFEST.json`
- `.delivery/plans/FATH-BOOTSTRAP/DOCUMENT_READ_ORDER.md` (this file)
- `.delivery/plans/FATH-BOOTSTRAP/REQUIREMENTS_TRACEABILITY.json`
- `.delivery/plans/FATH-BOOTSTRAP/PROJECT_MAP.md`
- `.delivery/plans/FATH-BOOTSTRAP/PROPAGATION_MAP.md` (AMENDMENT-002 §12 per-surface sweep — binding planning material, derives entirely from docs/34 + cited canonical text)
- `.delivery/plans/FATH-BOOTSTRAP/BOOTSTRAP_PLAN.md` (plan — operational, subject to independent review)
- `.delivery/plans/FATH-BOOTSTRAP/ROADMAP.md` (operational state, not new project authority)
- `.delivery/plans/FATH-BOOTSTRAP/TASK-001_PLAN.md` (task plan — subject to independent review)

## 5. Minimum re-orientation sequence for a bounded task (after bootstrap approval)

1. Control-plane governance + `BUILD_STATE.yaml` (section 0).
2. `AUTHORITY_MANIFEST.json` → verify hashes of the docs you will rely on.
3. Project-wide canonical set (section 1) — at minimum 00, 33 (AMENDMENT-001), 34 (AMENDMENT-002), 24, and the anti-drift rule in 23.
4. The task contract and approved task plan for the active task.
5. The task-specific canonical set (section 2) for the task's domain — read the actual sections cited by the task contract, not summaries.
6. Relevant source code, tests, and Git history in this repo.
