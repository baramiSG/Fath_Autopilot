# TASK-001 CI remediation — CI-9acd2c248926

**Role:** Implementer (REVIEW FINDINGS ADJUDICATION + REMEDIATION)
**Finding:** CI-9acd2c248926 (HIGH)
**Failed SHA:** `9acd2c2489264d0ea94c129a33ad27ab63f98738`
**Governed base:** `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`
**Authority:** TASK-001_PLAN.md §4.10 step 1 and A14 (CI asserts running interpreter is 3.11.x); `requires-python = ">=3.11,<3.12"` unchanged.

---

## Adjudication

| ID | Verdict | Evidence | Challenge |
|---|---|---|---|
| CI-9acd2c248926 | **VALID** | GitHub Actions job `sha-bound-evidence` (runs 33153025410 and 33153026521) executed `python --version` immediately after `astral-sh/setup-uv` with `python-version: "3.11"`. Logs show `Python 3.12.3` and `AssertionError: 3.12.3`. Env had `UV_PYTHON: 3.11`; later steps already use `uv run`. This is the GitHub `ubuntu-latest` default `python`, not a flake: both runs failed the same step in ~5–7s. Local reproduction: PATH `python` from an outer 3.12 venv printed `Python 3.12.13`; `uv python find --no-project --managed-python 3.11` plus PATH prepend made `python --version` print `Python 3.11.15` and the A14 assert pass. | Not a transient infrastructure failure. Not an A14 contract change. The 3.11 assertion is correct; the step invoked the wrong interpreter. |

---

## Correction

Keep A14 at full strength (`python --version` must be 3.11.x). After setup-uv, resolve the uv-managed 3.11 interpreter, put its `bin` on PATH (and `GITHUB_PATH`), then run the existing assert.

Regression: `test_ci_a14_binds_uv_managed_python_before_bare_python_assert` (failed on the pre-fix workflow; passes after).

Candidate stopped UNCOMMITTED on top of `9acd2c248926…`.
