# FATH-BOOTSTRAP — Remediation 4 Adjudication (review sequence 2, attempt-2 findings → plan V6)

**Project:** FATH_AUTOPILOT · **Scope:** FATH-BOOTSTRAP · **Plan version produced:** v6
**Role:** TASK_PLANNER / CHIEF_ARCHITECT (Claude Fable 5, 1M, Thinking ON, Max — inherited runtime)
**Input:** REJECT record `.delivery/reviews/FATH-BOOTSTRAP/plan-review-seq2-attempt-2.md` (commit `7883fae251856c1057f51d42f25261b4eb652f3a`), findings FATH-V5-001..005 against plan V5 commit `b4e392d33e98250114c82d695b0decda951c0164`.
**This is the FINAL correction of review sequence 2 (toward attempt 3 of 3). A rejection at attempt 3 becomes BLOCKED_FOR_SALIM.**

## Adjudication

| Finding | Verdict | Evidence and disposition |
|---|---|---|
| FATH-V5-001 (HIGH) — migration DML regex misses SQLAlchemy/Alembic API forms | **VALID — independently reproduced** | The planner re-tested the v5 pattern set (`\bINSERT\s+INTO\b`, `\bUPDATE\s+\w+\s+SET\b`, `\bDELETE\s+FROM\b`, `\bTRUNCATE\b`, `\bCOPY\s+\w+\s+FROM\b`, `bulk_insert`, `executemany`) against the two reviewer-cited forms `op.execute(sa.insert(t).values(…))` + `op.execute(sa.delete(t))`: **zero hits** (rg case-insensitive, exit 1). The v5 enumeration approach was structurally wrong for API-form DML. Replaced with an **AST-level allowlist detector** (TASK-001_PLAN §5 A13b-ii, rules R1–R4) plus six committed negative fixtures whose detection is asserted by a pytest module — the check is proven, not assumed, to fail on insert-then-delete. |
| FATH-V5-002 (HIGH) — A4 pre-binds index names only | **VALID** | v5 §6.0 bound only the six-name set; a name-correct index on the wrong column would have passed. §6.0 now pre-binds the **six full `pg_get_indexdef` definition strings** (uniqueness, table, btree access method, exact column, no predicate) compared by normalized string equality — the reviewer's suggested method, same style as the `pg_get_expr` default binding. Constraint comparison simultaneously made explicit at definition level (extracted enum value sets / numeric bounds / PK-UNIQUE column lists) — same defect class, closed in the same pass. |
| FATH-V5-003 (HIGH) — A15 verifies dependency names only | **VALID** | v5 A15 could pass with pydantic 1.x or SQLAlchemy 1.4 installed. §4.9 now pre-binds exact declared specifier strings — `pydantic>=2,<3`, `pydantic-settings>=2,<3`, `sqlalchemy>=2,<3` — AND requires resolved `uv.lock` majors = 2 for those three packages (mechanical `[[package]]` parse). Correctly noted: `uv lock --check` proves lock/metadata consistency, not that metadata requires the approved majors. Other dependencies carry no major contract (no authority binds one); disclosed as scope. |
| FATH-V5-004 (MEDIUM) — `redis:7` is a mutable tag | **VALID** | Docker tags are mutable; calling the tag "pinned" was wrong. Chose the reviewer-preferred option: **immutable digest pin** (`redis:<7.x.y>@sha256:<digest>` recorded in `docker-compose.yml`, same style as the PG base image); the implementer resolves and records the digest, A2 still verifies running major 7. Sweep of the same class: **GitHub Actions now pinned by full commit SHA** (§4.10 preamble) and **gitleaks pinned by version + verified sha256 checksum** (A9). No other mutable tags found. |
| FATH-V5-005 (LOW) — "15 named constraints" vs actual 13 | **VALID** | Mechanical recount of §6.0: PK + UNIQUE + 6 enum CHECKs + 5 numeric CHECKs = **13**. The erroneous "15" appeared in REMEDIATION-3_ADJUDICATION (V4-002 row) — corrected in place with a bracketed correction note; §6.0 and A4 now state the 13 count explicitly. The schema contract itself is unchanged. Sweep of other count claims (84 rows, 55 literals, 33 columns, 36 canonical docs): all verified correct. |

## Migration-DML detector design (FATH-V5-001)

AST-allowlist, not DML-form enumeration. Every migration file is parsed with Python `ast`; **R1**: every `op.<attr>()` call must be in the pre-bound DDL allowlist {create_table, drop_table, create_index, drop_index, create_check_constraint, drop_constraint, execute}; **R2**: `op.execute` accepts only a single plain string literal beginning with `CREATE|DROP|ALTER|COMMENT` (expression objects like `sa.insert(…)` fail structurally); **R3**: prohibited identifiers/attributes (`insert`, `update`, `delete`, `bulk_insert`, `executemany`, `exec_driver_sql`, `get_bind`, `merge`, `copy_expert`, `copy_from`) anywhere in any migration file including `env.py`; **R4**: no string literal may contain a DML statement pattern (catches raw SQL and DML smuggled after a DDL prefix). The reviewer-cited evasion fails three ways (R2 non-literal argument ×2, R3 `insert`, R3 `delete`). Six negative fixtures (`src/fath/tests/fixtures/negative_migrations/*.py.sample` — reviewer-cited form, `op.bulk_insert`, raw-SQL INSERT, `get_bind` connection execute, `t.insert()`, DDL-prefixed smuggle) are committed, and `src/fath/tests/unit/test_migration_dml_discipline.py` asserts real migrations PASS and **every fixture FAILS**. The design was executed during planning against all six fixtures plus a realistic migration-0001 shape (extensions, table, indexes, PL/pgSQL trigger body with internal semicolons): 6/6 fixtures detected, legitimate migration clean. `sa.text` is deliberately not prohibited (not a DML vector by itself; its abuse paths are closed by R2/R4).

## Artifact changes (v6)

| Artifact | Change |
|---|---|
| `TASK-001_PLAN.md` | v6 header/lineage/§12 (attempt 3 of 3 FINAL); §4.4 Redis digest pin; §4.9 pre-bound version contract; §4.10 actions-by-SHA + version-contract step + detector invocation + gitleaks checksum; §5 A13b-ii rebuilt as AST-allowlist detector R1–R4 + six negative fixtures; §6.0 six pre-bound `pg_get_indexdef` strings + 13-constraint count + definition-level constraint comparison method; §6.1 PERMITTED adds `negative_migrations/*.py.sample`; §6.2 A4(vii)(viii)/A9/A13/A15 corrected; §7 steps 6–7 updated |
| `BOOTSTRAP_PLAN.md` | v6 header/status/§14 (attempt 3 of 3 FINAL); §4.4 gitleaks checksum row; §6 Redis digest + version enforcement; §9 pipeline line (detector, index definitions, version contract, actions-by-SHA) |
| `REMEDIATION-3_ADJUDICATION.md` | V4-002 row: "15 named constraints" → **13** with bracketed correction note (FATH-V5-005); no other content touched |
| `PROPAGATION_MAP.md` | Header + consequences section version reference V5 → V6 (no row changes; 84 rows unchanged) |
| `PROJECT_MAP.md` | "plan-V5 state" → "plan-V6 state" (no structural change) |
| `REMEDIATION-4_ADJUDICATION.md` | This record (new) |
| `ROADMAP.md`, `REQUIREMENTS_TRACEABILITY.json`, `AUTHORITY_MANIFEST.json`, `DOCUMENT_READ_ORDER.md`, `V4_ADJUDICATION.md`, `REMEDIATION-1/2_ADJUDICATION.md` | Unchanged |

## Open items

No new OPEN items. FA-OPEN-020/022/023 unchanged. One disclosed scope note (not an OPEN item): dependencies other than pydantic/pydantic-settings/sqlalchemy carry no major-version contract because no authority or plan constraint binds one.

## Muhasib self-audit (summary)

- Every finding adjudicated against primary evidence; V5-001 reproduced mechanically before acceptance, and the replacement detector executed against all six evasions plus a legitimate migration before being bound into the plan.
- No oracle weakened; every change strengthens a check or corrects a factual claim. Schema contract content unchanged (V5-005 was a count error only).
- No production code written; the detector prototype was planning verification only — the implementer authors the actual test module per §5/§7.
- Attempt counter honest: this produces attempt 3 of 3 — FINAL; no counter reset, no renaming.
- Assumption disclosed: the six pre-bound `pg_get_indexdef` strings follow the stable PG16 rendering; a semantically-identical byte-form mismatch is a §9 stop condition, never a silent fixture pin.
