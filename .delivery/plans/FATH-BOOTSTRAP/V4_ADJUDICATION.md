# FATH-BOOTSTRAP — Plan V4: Adjudication of Plan-Review Attempt-3 Findings and AMENDMENT-002 Application

**Project:** FATH_AUTOPILOT · **Scope:** FATH-BOOTSTRAP · **Role:** CHIEF_ARCHITECT / TASK_PLANNER (Claude Fable 5, 1M, Thinking ON, Max — runtime inherited from the Claude Fable 5 Thinking Max parent controller; fresh context per RUNTIME_AUDIT_NOTE_001 and the corrected `model: inherit` seat configuration, control-plane commit `9ca49e7` / PR #12)
**Findings record adjudicated:** `.delivery/reviews/FATH-BOOTSTRAP/plan-review-attempt-3.md` (commit `ae8d7c8`, REJECT, 5 findings) against plan V3 commit `ca7228068b1723bb2e21d8b4ea0fd98eb6abe514`.
**Authority events since attempt 3:** escalation `FATH-BOOTSTRAP-ESCALATION-001` resolved by explicit owner decision; **AMENDMENT-002** transcribed as `docs/34_AMENDMENT_002_SOURCE_IDENTITY.md` (sha256 `0edb5245999e88382eab1c8a0f9679f45e60d3cd680903f3b56f3a3768dd9b99`, commit `af00923853e0234da403231258c822b949e9da00`, committed alone; hash re-verified byte-exact by this planner).
**Cycle status:** plan V4 opens a **fresh review sequence (attempt 1 of 3)** per Escalation Policy §6 — a human-approved change in project authority genuinely changed the planning scope and resolved the blocker that invalidated the previous sequence. The V1–V3 attempts, their reviews, both prior adjudications, and the exhausted-ladder escalation remain preserved unchanged; nothing is erased and no counter was reset by an agent (the reset is recorded in BUILD_STATE with the owner-decision trigger).

This record is planning material, not project authority; it approves nothing.

---

## FATH-P3-001 (BLOCKER) — source-identity model required human authority — **VALID; RESOLVED BY AMENDMENT-002 (human decision), not by planner argument**

**Finding recap:** the V3 dual-identifier design was "technically possible but not logically derived or fully propagated as claimed": no canonical document defined `slug`; doc 07 models `source_id` as Python `UUID`/TS `string`, so V3's blanket rule that event/UI `source_id: str` carries the slug conflicted with surviving UUID contracts; housing the textual identity in `slug` and redirecting doc-29 FKs were architecture proposals requiring human-approved authority under doc 23.

**Disposition:** VALID — and resolvable only by the owner, which is exactly what happened. The owner's decision is recorded as AMENDMENT-002 (docs/34, human-approved 2026-08-27). V4 does not re-argue the design; it applies the amendment as SPECIFIED authority:

- Identity model now SPECIFIED end-to-end (docs/34 §§1–11): `source_registry` single canonical table; `source_id UUID PK` immutable; `slug TEXT NOT NULL UNIQUE` (the amendment itself names the column); universal semantic rule; Pydantic `source_id: UUID` + separate `source_slug`; ALL persisted source FKs → `source_registry(source_id)`; doc-29 DDL superseded to UUID; YAML keys on `slug`; transport `source_id` strings are **serialized UUIDs** — the V3 "payload `source_id: str` carries the slug" rule (the core P3-001 defect) is reversed, and doc-07's Python-UUID/TS-string pairing is now exactly satisfied.
- The V3 proposal "doc-29 FKs → `source_registry(slug)`" is dead (docs/34 §§6–7 mandate UUID).
- §12 propagation sweep delivered as `PROPAGATION_MAP.md`: 69 individually cited surfaces across all thirteen §12 categories plus supplementary representations (Redis budget keys, metrics/log fields, CLI args, AGE `Source`-node properties, belief-calibration dicts, golden fixtures); zero blanket `str`-type assumptions; each remaining DERIVED application (PM-D15, PM-F2, PM-N1, PM-N2) states its derivation for reviewer inspection.
- §13 oracle delivered as TASK-001_PLAN A4: independently derived `expected_schema.json` proving UUID `source_id` PK, unique non-null `slug`, **no `sources` table** (negative query), **no FK targeting `slug`** + every FK referencing `source_registry` targets `source_id` (pg_constraint query), exact pinned normalized defaults, exact types/nullability, exact CHECK value set, doc-03 indices — plus negative INSERT tests.
- Classification hygiene: everything the amendment states is classified SPECIFIED (by AMENDMENT-002); nothing amendment-driven is presented as DERIVED and no DERIVED/PROPOSED residue is presented as SPECIFIED. Remaining PROPOSED element: only the *mechanism* `DEFAULT uuid_generate_v4()` (docs/34 §8 permits generated-or-assigned). FA-OPEN-021 reclassified RESOLVED_BY_AMENDMENT_002 in the traceability register.

**Artifacts:** BOOTSTRAP_PLAN §§2/3/4.1/4.3/7.4/12; PROPAGATION_MAP.md (new); TASK-001_PLAN §§2/4.6/4.7/6.2-A4; AUTHORITY_MANIFEST (FA-DOC-34, PREC-00, relationship updates); DOCUMENT_READ_ORDER (34 in always-read set); REQUIREMENTS_TRACEABILITY (FA-OPEN-021 resolved; FA-REQ-W1-001/002 rewritten; FA-REQ-AM-003 added); ROADMAP (AMENDMENT-002 verifier line; TASK-001/006 rows).

## FATH-P3-002 (HIGH) — acceptance criteria tolerated wrong versions/defaults/boundaries; no Python/dependency check — **VALID; corrected**

**Finding recap:** A2 did not verify running Postgres/Redis major versions; A4 compared only default *presence*, so wrong default values passed; A6 omitted documented numeric boundaries and exact default behavior; no criterion verified Python 3.11 or the dependency allowlist/prohibitions.

**Corrections (TASK-001_PLAN v4):**
- **A2** now verifies the RUNNING versions, not just image pins: `current_setting('server_version_num')::int ∈ [160000, 170000)` (Postgres major 16, doc 28) and Redis `INFO server` major 7 — in addition to extension presence.
- **A4** now compares **exact normalized DB default expressions** (`pg_get_expr` output string-compared against pinned expected values) for the two columns that carry DB defaults (`status` → `'candidate'` SPECIFIED by doc 24 §1; `source_id` → `uuid_generate_v4()` PROPOSED, pinned), and asserts **every other column has NO DB default** — so an incorrect or drifted default value fails, not just a missing one. Types/nullability/CHECK value set/indices are compared exactly per the cited fixture.
- **A6** now asserts **every doc-03 model default exactly** (30 / 200 / 500_000_000 / UNKNOWN / NONE / 0.70 / 0.50 / True / "unknown") and tests **documented numeric boundaries at below/at/above** per Oracle Policy §10 (confloat 0–1 fields accept 0 and 1, reject −0.001 and 1.001; conint ge=0 fields accept 0, reject −1).
- **New A14:** running interpreter asserted 3.11.x in CI + `requires-python = ">=3.11,<3.12"` verified by test (Python 3.11 remains PROPOSED in BOOTSTRAP_PLAN §4.4; A14 enforces the approved plan's contract mechanically).
- **New A15:** dependency/environment contract — exact permitted direct-dependency lists (runtime + dev) and prohibited-name list written into the plan (TASK-001_PLAN §4.9); mechanical comparison against `pyproject.toml`; prohibited-name scan over `pyproject.toml` AND `uv.lock` (covers transitive smuggling); lock integrity via `uv sync --frozen` (A1). Transitive-resolution limitation stated per Oracle Policy §48.

## FATH-P3-003 (HIGH) — no-seed verification evadable; marker was self-attestation — **VALID; corrected with non-attestational checks**

**Finding recap:** A12 proved only two empty fresh-schema states; A13 checked filenames and a candidate-authored marker; seed constants/loader behavior could hide in permitted files under neutral names; authoritative IDs could sit inside a marker-bearing fixture.

**Corrections (TASK-001_PLAN §5 + A12/A13, all mechanical and independent of candidate attestation):**
- **A12 third measurement point:** zero-row check now ALSO runs **after the complete pytest session against the same database** — fixture non-persistence is proven by observation of final DB state, not inferred from a marker (plus the existing fresh-head and post-cycle checks). Runs as CI-level SQL outside pytest.
- **A13a authoritative-literal value scan:** word-boundary, case-insensitive scan of every tracked file (`git ls-files`, carve-outs: `docs/**`, `.delivery/**`, and the single cited scan-list fixture) for the authoritative identity literals themselves — the 7 doc-24 §1 slugs, doc-30 Tier-1/2 slugs, and the 16 doc-03 seed names. Production seed identities are detected **by value in any file under any neutral variable/file name** — the named evasion path. The scan list contains identities only (never FA-OPEN-020 values); the root README is inside the scan domain.
- **A13b registry-write discipline:** outside migrations and tests, no tracked `src/` file may contain `source_registry` write patterns (INSERT/insert()/.add()/executemany/COPY) — mechanical scan; migration 0001's own zero-insert property is what A12 proves.
- **A13c import discipline:** DB-access imports (`sqlalchemy`/`asyncpg`/`psycopg`/`alembic`) permitted only in `db/connection.py`, migrations, and tests; every `__init__.py` empty/docstring-only; the models file pydantic-only. In this bounded candidate, an effective "loader under a neutral name" cannot exist without violating A13b or A13c.
- **A13d fixture syntheticity by content rules:** fixtures must contain zero authoritative literals, only RFC-2606 reserved domains in URLs, and `synthetic_`-prefixed slug values — syntheticity established by checkable content properties. The v3 marker is demoted to non-evidentiary labeling.
- **Honest limitation (Oracle Policy §48):** the scans detect plaintext/normalized forms; deliberate obfuscation (encoding, dynamic construction) is outside their mechanical reach and is covered by the independent reviewer's inspection of the actual diff — where obfuscation would itself be dispositive evidence. This limitation is stated in the plan rather than papered over.

## FATH-P3-004 (HIGH) — tree-oracle scan domain and `__init__.py` permission under-specified — **VALID; corrected**

**Finding recap:** unqualified "`__init__.py` files" permitted noncanonical paths such as `rogue/__init__.py`; the scan universe was not fixed to the tracked Git tree, so filesystem artifacts (`.venv`, caches) would pollute the check.

**Corrections (TASK-001_PLAN §6.1):**
- **Scan domain fixed:** the comparison set `P` is exactly the output of `git ls-files` at the candidate SHA (normalized tracked Git tree). Untracked filesystem state can never enter `P`; CI runs on a clean checkout. `docs/**` and `.delivery/**` are explicit carve-outs governed by the separate A16 diff-boundary check.
- **Every pattern anchored:** the manifest prohibits unanchored patterns by rule. `__init__.py` is permitted ONLY at the enumerated parents (`src/fath/`, the 17 named module/model dirs, migrations dirs, tests dirs) — `rogue/__init__.py` or `src/fath/llm/__init__.py` fails the `P ⊆ REQUIRED ∪ PERMITTED` condition because no anchored entry matches it. Migration versions, test files, fixtures, docker init files, and tool configs are all anchored globs at named parents; PROHIBITED adds explicit fail-fast entries (non-doc-16 first segments under `src/fath/`, top-level `tests/`/`migrations/`, `sources_seed.yaml`, `*seed*` under `src/`, any second migration file).

## FATH-P3-005 (MEDIUM) — `.delivery/` scope vs evidence-writing contradiction — **VALID; corrected**

**Finding recap:** TASK-001 §4.1 said `.delivery/` remains untouched while §10 required the implementer to write evidence under `.delivery/evidence/TASK-001/`.

**Correction (TASK-001_PLAN §§4.1/10 + new A16):** the boundary is now single-sourced and mechanical. **Writer:** the implementer (Role & Model Policy §8 assigns evidence creation to the implementer; Oracle Policy §46 requires a defined location). **Location:** exactly `.delivery/evidence/TASK-001/`, additions only — included in the allowed-file scope in §4.1 as the single authorized `.delivery/` write. **Enforcement:** A16 diff-boundary check — the candidate diff vs PR base must show zero paths under `docs/` and only `^\.delivery/evidence/TASK-001/` additions under `.delivery/` (no modification/deletion of plans/reviews/escalations/audit/state). The A5 tree oracle carves both prefixes out of its domain, so the two checks compose without contradiction.

---

## Regression sweep (V1/V2-resolved findings — verified preserved in V4)

| Resolved finding | V4 status |
|---|---|
| PR-002 (doc-16 layout + ADR rule) | Preserved — §4.1 doc-16-exact scaffold; anti-drift stop condition 4 retained and extended with the docs/34 §6 FK rule |
| PR-003 (A8 scoped scan; A9 gitleaks oracle) | Preserved verbatim — A8 scope/exclusions unchanged; A9 pinned gitleaks unchanged |
| PR-004 (Week-1 zero-LLM posture = PROPOSED with defined behavior + alternative) | Preserved verbatim — BOOTSTRAP_PLAN §4.4; ROADMAP Week-1 header |
| PR-005 (PG image = PROPOSED, pinned, functional checks A11) | Preserved verbatim — BOOTSTRAP_PLAN §4.4; TASK-001 A11; A2 additionally verifies running versions (strengthens, does not weaken) |
| PR-006 → P2-004 (CI = SHA-bound evidence, never trusted; GATE-SETUP sequenced before ANY merge eligibility; candidates halt at REVIEW_APPROVED; no review-plus-controller substitute; no unverified protection claims) | Preserved verbatim — BOOTSTRAP_PLAN §9; TASK-001 §11; ROADMAP governance; FA-REQ-CP-001/CP-003. Attempt-3 review confirmed P2-004 RESOLVED; V4 changes none of that language |
| PR-007 (production auth OPEN per docs/33; ADRs require human approval) | Preserved — FA-REQ-W5-001, FA-OPEN-004/011 unchanged |
| PR-001/P2-002 seed-value gating (FA-OPEN-020, Salim; TASK-006 gate; no invented values) | Preserved and explicitly restated: AMENDMENT-002 resolves identity semantics only; base URLs/tiers/rate limits/collection modes remain OPEN behind FA-OPEN-020 |
| P2-001/P2-003 lineage | Superseded by stronger V4 treatments above (identity now SPECIFIED by docs/34; tree oracle now domain-fixed and anchored) |

**Roadmap dependencies:** unchanged by AMENDMENT-002 — TASK-006 still gated on FA-OPEN-020; GATE-SETUP still gates every merge; Week-1 graph identical. Verified row-by-row during the ROADMAP edit.

**Runtime note:** this planning session runs as a fresh subagent context inheriting the parent controller's Claude Fable 5 Thinking Max runtime (post-PR-#12 `model: inherit` seats). Historical V1–V3 artifacts and their self-reported runtime lines are untouched per RUNTIME_AUDIT_NOTE_001 and the owner's directive (docs/34 §14).

## Artifacts changed in V4

| Artifact | Change |
|---|---|
| PROPAGATION_MAP.md | **NEW** — docs/34 §12 full-corpus per-surface sweep (69 surfaces, 13 §12 categories + supplementary), binding on task plans |
| V4_ADJUDICATION.md | **NEW** — this record |
| TASK-001_PLAN.md | Rewritten v4: docs/34 identity model + §13 A4 oracle; A2 running versions; A4 exact normalized defaults; A6 defaults+boundaries; A5 git-tree domain + anchored sets; A12 three-point zero-row; A13a–d value/behavior/content scans; new A14 (Python 3.11), A15 (dependency contract), A16 (diff boundary); §10 evidence writer/location; fresh-cycle attempt numbering |
| BOOTSTRAP_PLAN.md | v4: header + amendment block; §§1–3 authority/readiness/contradictions (FA-OPEN-021 resolved); §4.1 identity row SPECIFIED; §4.3 dual-identifier row removed, DERIVED docs/34 applications row added; §4.4 uuid-default proposal added; §6 dependency contract pointer; §7.4 rewritten on docs/34 + PROPAGATION_MAP; §9 pipeline pointer to TASK-001 §4.10; §12 open items; §14 fresh-cycle numbering |
| AUTHORITY_MANIFEST.json | FA-DOC-34 entry (tier 1, HUMAN_APPROVED_AMENDMENT, sha256); PREC-00 rule; amendment_002_commit; PREC-0/PREC-1 wording; relationship updates on FA-DOC-33/03/24/29/30/06/07 |
| DOCUMENT_READ_ORDER.md | doc 34 in the always-read project-wide set (position 3, after 33); source-identity task-domain row; PROPAGATION_MAP listed as navigation aid; re-orientation minimum includes 34; amendment commits in header |
| REQUIREMENTS_TRACEABILITY.json | FA-OPEN-021 → RESOLVED_BY_AMENDMENT_002; FA-REQ-W1-001/002 rewritten under docs/34; new FA-REQ-AM-003; FA-OPEN-006 partial resolution note; amendment_002_commit + amendment_note |
| PROJECT_MAP.md | Header precedence; §4 identity block + corrected FK notes; §9 authority pointers (34 rows) |
| ROADMAP.md | AMENDMENT-002 verifier line in governance; TASK-001/TASK-006 rows updated; FA-OPEN-021 marked resolved in open items; dependency-invariance note; amendment commits in header |
| REMEDIATION-1_ADJUDICATION.md, REMEDIATION-2_ADJUDICATION.md | **Unchanged** (history) |

## Open items after V4

- **FA-OPEN-020** — OPEN (Salim): 16-row seed value table + Tier-0 onboarding checklists; gates TASK-006 → 007/008/014. Unchanged.
- **GATE-SETUP** — pending (Salim): branch protection + trusted exact-identity verification + receipts; gates every merge. Unchanged.
- **FA-OPEN-021** — RESOLVED_BY_AMENDMENT_002.
- All other FA-OPEN items unchanged from V3 (see BOOTSTRAP_PLAN §12).

A rejection of this plan (attempt 1 of the fresh sequence) returns to planner remediation per Escalation Policy §10; the sequence limit remains 3 with `BLOCKED_FOR_SALIM` after a third rejection.
