# TASK-001 CI remediation — CI-fa0b2a49416f

**Role:** Implementer (REVIEW FINDINGS ADJUDICATION + REMEDIATION)
**Finding:** CI-fa0b2a49416f (HIGH)
**Failed SHA:** `fa0b2a49416f5f885672ed48b21122a75d802a6a`
**Governed base:** `2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9`
**Authority:** TASK-001_PLAN.md §4.10 step 1 and A14 (running interpreter is 3.11.x). A14 assertion not weakened.

---

## Adjudication

| ID | Verdict | Evidence | Challenge |
|---|---|---|---|
| CI-fa0b2a49416f | **VALID** | Runs 33155528731 and 33155532077 failed the A14 step with `uv python find --no-project --managed-python 3.11` → `error: No interpreter found for Python 3.11 in virtual environments or managed installations` (exit 2). Env had `UV_PYTHON=3.11` and `UV_PYTHON_INSTALL_DIR` set by setup-uv; no project venv exists yet (`uv sync` is the next step). Local reproduction: empty `UV_PYTHON_INSTALL_DIR` produced the same error and FIND_RC=2. `uv python find` does not download. Not a flake (two runs, ~8s). | Not transient infrastructure. A14 remains 3.11.x. The prior PATH-bind used `find` without `install`. |

---

## Correction

Keep `python --version` / `sys.version_info[:2] == (3, 11)`. Before find, run `uv python install --managed-python --no-bin 3.11` (respects `UV_PYTHON_INSTALL_DIR`). Then PATH/`GITHUB_PATH` bind as before.

Regression test now requires `uv python install` before `uv python find` (RED on pre-fix workflow, GREEN after). Empty-dir install+find yielded Python 3.11.15.

Candidate stopped UNCOMMITTED. HEAD remains `fa0b2a49416f…`.
