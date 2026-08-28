# TASK-001 Remediation 2 — Finding Adjudication

**Role:** Implementer (REMEDIATE, round 2 of 2 — FINAL normal round)
**Task:** TASK-001 — Repository Foundation
**Review record:** control-plane `implementation-review-attempt-2.md` (Sol REJECT, 3 HIGH findings; attempt-1 findings independently CLOSED)
**Governed base / HEAD:** `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9` (unchanged; candidate remains UNCOMMITTED)
**Policy:** Autonomous Delivery Policy V2 §13; IAC-001 residual-limit rule; Oracle Policy §§7, 11, 37–39

---

## Orientation receipt

- Authority reread: `TASK-001_PLAN.md` v6 (§5 R2/R4, A13, §6.0 constraint comparison, §6.1/A5, §10); `TASK-001-IAC.md` IAC-001 residual-limit; Oracle Policy §§7, 11, 37–39; attempt-2 review record; remediation-1 adjudication (closed findings not reopened).
- Repository inspected: detector `check_source` / `DML_IN_STRING`; A4 `assert_constraint_semantics`; A5 `fnmatch` matcher; negative fixtures N1–N14; live HEAD `2649fb91…`; 86 untracked files at intake; live PostgreSQL (count 0).
- Persona: PostgreSQL SQL-static-analysis and schema/path-oracle remediator.
- Skills invoked: sanad, muhasib, task-standards, project-orientation, receiving-code-review, test-driven-development, systematic-debugging, verification-before-completion.

---

## Adjudication

| ID | Verdict | Reproduced evidence | Challenge |
|---|---|---|---|
| FATH-IMPL-005 | **VALID** | `INSERT/**/INTO` / `DELETE/**/FROM` inside a DDL-prefixed `op.execute` string returned **zero** detector violations. The same SQL executed on PostgreSQL as `INSERT 0 1` then `DELETE 1`, leaving `source_registry` count 0 (then rolled back). PL/pgSQL `EXECUTE 'INSERT' \|\| ' INTO …'` and variable-assembled `EXECUTE stmt` also returned zero violations. Standalone `op.execute("INSERT/**/INTO …")` was already rejected by R2 (non-DDL prefix); the demonstrated hole is comment-separated / server-dynamic DML **inside** a DDL-prefixed string, which also defeats A12 insert-then-delete. | None on the defect. Mechanism chosen: comment-normalize SQL (replace `--` / nested `/* */` with a space so `INSERT/**/INTO` becomes `INSERT INTO`), scan individual and `\|\|`/adjacent concatenated SQL string literals after the same normalization, and reject PL/pgSQL `EXECUTE` that is not `EXECUTE FUNCTION` / `EXECUTE PROCEDURE`. Legitimate `CREATE FUNCTION fath_source_id_immutable()` and `CREATE TRIGGER … EXECUTE FUNCTION` remain clean. |
| FATH-IMPL-006 | **VALID** | Installing `CHECK (source_class = ANY (ARRAY[<nine expected literals>, source_class]))` in a disposable schema rendered `pg_get_constraintdef` with the column name inside the array. `assert_constraint_semantics` **accepted** it. Inserting `'not_a_real_class'` succeeded (self-referential allowlist). Analogous `lower('…')` and `NULL` array elements were also accepted by A4. The live `IN (…)` schema still rejects `'not_a_real_class'`. | None on the defect. Mechanism: parse the complete `ARRAY[…]` body and require every element to be a quoted constant whose set equals the pre-bound values — no column references, NULLs, functions, or other expressions. |
| FATH-IMPL-007 | **VALID** | Python `fnmatch` treated `/` as ordinary text: `docker/postgres/*.sql` matched `docker/postgres/nested/unauthorized.sql`; `src/fath/tests/unit/test_*.py` matched `src/fath/tests/unit/test_nested/unauthorized.py`; fixture JSON / `.py.sample` / integration `test_*.py` likewise. The full A5 extras check would therefore accept nested unauthorized paths. | None on the defect. Mechanism: segment-aware POSIX matching (`*` cannot cross `/`). Manifest globs were already last-segment stars; after the matcher change the real candidate tree still has zero extras. |

Attempt-1 findings FATH-IMPL-001..004 were not reopened. All five prior bypass probes remain caught; N1–N14 still fail; real migrations and the legitimate DDL corpus still pass.

---

## What changed

### FATH-IMPL-005
- Hardened string-literal DML analysis in `src/fath/tests/unit/test_migration_dml_discipline.py`: `normalize_sql_comments`, concatenated-literal DML scan, dynamic `EXECUTE` ban with trigger-syntax exception.
- Negative fixtures N15 (comment-separated DML) and N16 (PL/pgSQL dynamic EXECUTE). Inline SQL-token evasion probes (comment forms + concat + variable EXECUTE).
- Integration proving test executes the insert/delete specimen against PostgreSQL and requires detector rejection.

### FATH-IMPL-006
- `assert_constraint_semantics` now splits the enum `ARRAY[…]` and requires quoted constants only.
- Proving tests: self-referential definition; `lower()` and `NULL` variants; disposable-schema install with A4 rejection, demonstration that self-ref accepts a bogus value, and that a correct `IN (…)` constraint still rejects it.

### FATH-IMPL-007
- Replaced full-path `fnmatch` with `posix_path_match` (per-segment). Required glob matching and the `0001_*.py` assertion use the same matcher.
- Proving tests inject a nested path under every single-level REQUIRED/PERMITTED glob and require rejection; immediate children still match.

### Evidence / tree
- New fixtures match `negative_migrations/*.py.sample`; new integration test matches `src/fath/tests/integration/test_*.py`. No `expected_tree.json` pattern change required under segment-aware matching (real-tree extras = []).
- Evidence under `.delivery/evidence/TASK-001/` refreshed; this adjudication file added.
- `BASE_SHA.txt` unchanged (`2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`).

---

## Proving tests

| Finding | Tests |
|---|---|
| 005 | `test_every_negative_fixture_n1_through_n16_fails`; `test_sql_token_evasion_probes_are_rejected`; `test_comment_separated_insert_delete_executes_and_is_detected`; `test_every_real_migration_file_passes`; `test_legitimate_ddl_corpus_passes`; `test_reviewer_bypass_probes_are_rejected` |
| 006 | `test_a4_rejects_self_referential_enum_definition`; `test_a4_rejects_nonconstant_enum_array_definition`; `test_a4_rejects_self_referential_and_nonconstant_enum_in_disposable_schema`; `test_a4_expected_schema`; `test_negative_bogus_status` |
| 007 | `test_a5_rejects_nested_paths_under_single_level_globs`; `test_a5_permits_immediate_children_of_single_level_globs`; `test_expected_tree_conformance` |

Candidate stopped UNCOMMITTED. HEAD remains `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`.
