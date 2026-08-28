# TASK-001 Remediation 3 — Finding Adjudication (FATH-IMPL-008)

**Role:** Implementer (REVIEW FINDINGS ADJUDICATION + REMEDIATION; interrupted-rescue completion)
**Task:** TASK-001 — Repository Foundation
**Finding:** FATH-IMPL-008 (HIGH)
**Governed base / HEAD:** `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9` (unchanged; candidate remains UNCOMMITTED)
**Policy:** Autonomous Delivery Policy V2 §13; IAC-001 residual-limit rule; plan §5 A13b-ii R1–R4

---

## Orientation receipt

- Authority reread: `TASK-001_PLAN.md` v6 §5 R2/R4, A12, A13; `TASK-001-IAC.md` IAC-001 residual-limit (a new evasion class in the artifact is a normal implementation finding); docs/34 source identity; real `0001_source_registry.py`.
- Repository inspected: live detector `DML_IN_STRING` (plan R4 regex, unmodified); `sql_executed_statements_all_ddl` statement-head allowlist already present on the interrupted-rescue candidate; N17/N18 fixtures; `test_qualified_copy_update_dml.py`; HEAD `2649fb91…`; 93 untracked files at intake of this seat.
- Persona: PostgreSQL SQL-static-analysis remediator for Alembic DML-discipline oracles.
- Skills invoked: receiving-code-review, test-driven-development, systematic-debugging, sanad, sanad-provenance, muhasib, muhasabah-gate, al-muhasibi, verification-before-completion, task-standards.

---

## Adjudication

| ID | Verdict | Reproduced evidence | Challenge |
|---|---|---|---|
| FATH-IMPL-008 | **VALID** | Plan R4 regex `DML_IN_STRING` (`COPY\s+\w+\s+FROM`, `UPDATE\s+\w+\s+SET`) returns **no match** for (a) `COPY public.source_registry (…) FROM PROGRAM`, (b) `COPY "public"."synthetic_copy_probe" (…) FROM PROGRAM`, (c) `UPDATE ONLY public… SET`. After `\w+` consumes `public` / `ONLY`, the next token is `.` or the table name, not `FROM`/`SET`. Live PostgreSQL executed the reviewer COPY form as `COPY 1`; savepoint rollback restored count 0 (A12 concealment); live `UPDATE ONLY … SET` returned `UPDATE 1`. | None on the defect. Mechanism already present on the interrupted-rescue tree and preserved: conservative statement-head allowlist (`CREATE`/`DROP`/`ALTER`/`COMMENT` only) after top-level `;` split that respects quotes, dollar-quotes, and comments. That rejects COPY (any qualification, quoting, column list, `FROM PROGRAM`/`STDIN`), `UPDATE ONLY`, and transaction-control concealment (`SAVEPOINT`/`ROLLBACK`) by construction. Plan R4 regex was **not** rewritten (plan-specified; allowlist is the additional layer the required_correction permits). |

---

## What changed this seat (preserve justified rescue; do not rewrite)

**Preserved from the interrupted rescue (not rewritten):**

- `sql_executed_statements_all_ddl` / `_split_top_level_sql_statements` / `_statement_head` in `src/fath/tests/unit/test_migration_dml_discipline.py`, wired into `check_source` for every `op.execute` string **in addition to** R2 `DDL_PREFIX` and R4 `DML_IN_STRING`.
- Negative fixtures `N17_qualified_copy_from_program.py.sample` and `N18_update_only_set.py.sample`.
- Live integration module `src/fath/tests/integration/test_qualified_copy_update_dml.py` (COPY 1 / UPDATE 1 / savepoint concealment + detector rejection).

**Completed remaining defects / proving tests:**

- Quoted-identifier COPY probe in `STATEMENT_ALLOWLIST_PROBES`.
- `test_r4_regex_misses_impl008_forms_allowlist_still_rejects` pins that R4 still misses the demonstrated forms while the allowlist rejects them.
- Integration tests now also pass the **exact live-executed** COPY SQL and the live `UPDATE ONLY` SQL through `check_source`.
- Evidence under `.delivery/evidence/TASK-001/` refreshed, including checksum-verified gitleaks 8.30.1 (`no leaks found`) and this adjudication file.

Real migration `0001_source_registry.py` and the legitimate function/trigger DDL corpus still pass the detector.

---

## Proving tests

| Finding | Tests |
|---|---|
| 008 | `test_every_negative_fixture_n1_through_n18_fails`; `test_statement_allowlist_probes_are_rejected`; `test_r4_regex_misses_impl008_forms_allowlist_still_rejects`; `test_qualified_copy_from_program_executes_is_concealed_and_is_detected`; `test_update_only_set_executes_live_and_is_detected`; `test_every_real_migration_file_passes`; `test_legitimate_ddl_corpus_passes` |

Candidate stopped UNCOMMITTED. HEAD remains `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`.
