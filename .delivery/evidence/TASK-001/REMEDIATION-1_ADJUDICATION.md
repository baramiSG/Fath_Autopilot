# TASK-001 Remediation 1 — Finding Adjudication

**Role:** Implementer (REMEDIATE, round 1 of 2)
**Task:** TASK-001 — Repository Foundation
**Review record:** control-plane `implementation-review-attempt-1.md` (Sol REJECT, 4 HIGH findings)
**Governed base / HEAD:** `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9` (unchanged; candidate remains UNCOMMITTED)
**Policy:** Autonomous Delivery Policy V2 §13; severity taxonomy §4

---

## Orientation receipt

- Authority reread: `TASK-001_PLAN.md` v6 (§5 A13b-ii, §6 A4/A6/A7, §6.0 constraint comparison, §6.1 tree, §10 evidence); `TASK-001-IAC.md` IAC-001; docs/03 field defaults; docs/34 identity; review attempt-1 record.
- Repository inspected: detector, schema oracle, `pyproject.toml` mypy config, `SourceRegistryRecord`, negative fixtures N1–N9, live HEAD/untracked identity (80 files at intake).
- Persona: Alembic/PostgreSQL contract-oracle and typed-Python CI remediator.
- Skills invoked: sanad, muhasib, task-standards, project-orientation, receiving-code-review, test-driven-development, systematic-debugging, verification-before-completion.

---

## Adjudication

| ID | Verdict | Reproduced evidence | Challenge |
|---|---|---|---|
| FATH-IMPL-001 | **VALID** | Combined probes with `.replace`-assembled DML returned **zero** detector violations for `import alembic.op as o2`, `run = op.execute`, `operator.attrgetter("execute")`, and `connection.execute(...)` in env.py-shaped code. Canonical `op.execute("XNSERT…".replace(…))` was already caught by R2 (non-literal argument); the failure scenario is the unrecognised-sink + replace combination, which fully bypassed R1–R4. | None on the defect. Mechanism chosen: whole-file import allowlist, execution-sink allowlist (`op.execute` only in version scripts; none in env.py), callable-alias ban, `.replace` assembly ban (Constant.replace everywhere; all replace in version scripts). `env.py` `raw_url.replace` for URL conversion remains allowed. |
| FATH-IMPL-002 | **VALID** | Current A4 numeric check accepted `CHECK ((max_requests_per_minute >= 0 AND max_requests_per_minute <> 29))` (fragment match). Wrong-column-only `CHECK ((max_pages_per_cycle >= 0))` was already rejected by `column in compact`. Enum extra predicates without extra quotes (`AND length(status) > 0`) preserved the value set. CHECK `conkey` columns were compared only for PK/UNIQUE. | Wrong-column-only was already caught; extra-predicate and missing CHECK column equality were not. Required correction (complete normalized semantics including columns and absence of extra predicates) is implemented in full. |
| FATH-IMPL-003 | **VALID** | Governed `uv run mypy src/` reported `Success: no issues found in 25 source files` while `src/` contains 39 `.py` files. `pyproject.toml` `[tool.mypy] exclude = ["src/fath/tests"]`. Passing all 39 files explicitly surfaced 7 strict errors in `test_expected_tree.py` (reviewer also cited `test_settings.py:15,41`; with the pydantic mypy plugin those two did not reproduce as errors). | `test_settings.py` did not error under this candidate’s pydantic plugin. Exclusion and `test_expected_tree.py` errors are valid. Exclusion removed; all 39 files now type-check with zero errors. |
| FATH-IMPL-004 | **VALID** | `test_doc03_field_defaults` omitted `api_base_url`, `robots_url`, `terms_url`, `subscription_name`, `country_scope`, `topic_scope`, `independence_group`, `data_quality_notes`, `legal_notes`, `last_access_review_at`, and `status`. Mutating `data_quality_notes` left the existing default test green. Missing-field case used `name=None` rather than omitting the key. | None. |

---

## What changed

### FATH-IMPL-001
- Hardened `check_source` in `src/fath/tests/unit/test_migration_dml_discipline.py`: canonical import allowlist (`from alembic import op` and optional `import sqlalchemy as sa` in version scripts; env.py’s four existing imports); execution-sink allowlist; callable-alias ban; `attrgetter`/`itemgetter`/`methodcaller` as dynamic dispatch; `.replace` SQL assembly ban.
- Negative fixtures N10–N14 plus inline reviewer-bypass probes. N1–N9 still fail; real migrations and the legitimate DDL corpus still pass.

### FATH-IMPL-002
- Extracted `assert_constraint_semantics`; A4 now requires `conkey` column lists for every constraint and exact normalized CHECK text (no extra predicates).
- `expected_schema.json` transcribes constrained columns for all 13 constraints.
- Proving tests: extra-predicate definition, wrong-column definition, disposable-schema extra-predicate and wrong-column.

### FATH-IMPL-003
- Removed `[tool.mypy] exclude`.
- Typed `test_expected_tree.py` manifest loading.
- Config proving test: mypy exclude must not mention tests.
- `uv run mypy src/` → 39 files, 0 errors.

### FATH-IMPL-004
- Table-driven assertion of every doc-03 default plus `status` and dynamic `source_id`.
- Parametrized mutation oracle over every defaulted field.
- Missing-required case omits `name`; `name=None` retained as a separate null test.

### Evidence / tree
- New fixtures match existing `negative_migrations/*.py.sample` permitted glob; no `expected_tree.json` pattern change required.
- Evidence under `.delivery/evidence/TASK-001/` refreshed; this adjudication file added.

---

## Proving tests

| Finding | Tests |
|---|---|
| 001 | `test_every_negative_fixture_n1_through_n14_fails`; `test_reviewer_bypass_probes_are_rejected`; `test_every_real_migration_file_passes`; `test_legitimate_ddl_corpus_passes` |
| 002 | `test_a4_rejects_extra_predicate_definition`; `test_a4_rejects_wrong_column_definition`; `test_a4_rejects_extra_predicate_and_wrong_column_in_disposable_schema`; `test_a4_expected_schema` |
| 003 | `test_mypy_config_does_not_exclude_tests`; governed `uv run mypy src/` |
| 004 | `test_doc03_field_defaults`; `test_altered_default_fails_oracle[*]`; `test_missing_required_field_rejected` |

Candidate stopped UNCOMMITTED. HEAD remains `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`.
