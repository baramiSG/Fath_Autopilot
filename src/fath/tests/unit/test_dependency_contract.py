"""A14/A15 dependency and Python runtime contract."""

from __future__ import annotations

import re
import sys
import tomllib

from fath.tests.conftest import REPO_ROOT

REQUIRED_RUNTIME = {
    "pydantic",
    "pydantic-settings",
    "sqlalchemy",
    "alembic",
    "asyncpg",
    "redis",
    "pyyaml",
}
REQUIRED_DEV = {"pytest", "pytest-asyncio", "ruff", "mypy", "types-pyyaml"}
OPTIONAL = {"psycopg", "testcontainers", "greenlet"}
_AZ = "azure"
VERSION_CONTRACT = {
    "pydantic": ">=2,<3",
    "pydantic-settings": ">=2,<3",
    "sqlalchemy": ">=2,<3",
}
PROHIBITED = {
    "fastapi",
    "langgraph",
    "prefect",
    "openai",
    _AZ + "-openai",
    "anthropic",
    "transformers",
    "torch",
    "sentence-transformers",
    "vllm",
    "unstructured",
    "paddleocr",
}


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _split_dep(item: str) -> tuple[str, str]:
    item = item.strip()
    match = re.match(r"^([A-Za-z0-9._-]+)(?:\[[^\]]+\])?(.*)$", item)
    assert match is not None, item
    name, spec = match.group(1), match.group(2).strip()
    spec = re.sub(r"\s+", "", spec)
    return _normalize(name), spec


def test_mypy_config_does_not_exclude_tests() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    mypy = data.get("tool", {}).get("mypy", {})
    exclude = mypy.get("exclude", [])
    if isinstance(exclude, str):
        exclude = [exclude]
    assert not any("tests" in str(item) for item in exclude)


def test_requires_python_is_311_band() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["requires-python"] == ">=3.11,<3.12"


def test_running_interpreter_is_311() -> None:
    assert sys.version_info[:2] == (3, 11)


def test_ci_a14_binds_uv_managed_python_before_bare_python_assert() -> None:
    """A14 must not invoke the GitHub runner's default ``python``.

    ``astral-sh/setup-uv`` with ``python-version: "3.11"`` sets ``UV_PYTHON`` but
    does not replace PATH ``python``. GitHub ``ubuntu-latest`` currently ships
    CPython 3.12 as ``python``; CI runs 33153025410 and 33153026521 failed with
    ``AssertionError: 3.12.3`` on the bare ``python --version`` step.
    """

    text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    marker = "Assert running interpreter is 3.11.x"
    assert marker in text
    start = text.index(marker)
    rest = text[start:]
    run_idx = rest.index("run:")
    after_run = rest[run_idx:]
    next_step = after_run.find("\n      - name:")
    script = after_run if next_step == -1 else after_run[:next_step]
    find_idx = script.find("uv python find")
    version_idx = script.find("python --version")
    assert find_idx != -1, "A14 must resolve uv-managed 3.11 before asserting python --version"
    assert "--managed-python" in script
    assert "3.11" in script
    assert version_idx != -1
    assert find_idx < version_idx
    assert "sys.version_info[:2] == (3, 11)" in script
    assert "PATH" in script
    assert "GITHUB_PATH" in script


def test_dependency_contract_names_and_versions() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    runtime = dict(_split_dep(item) for item in data["project"]["dependencies"])
    dev = dict(_split_dep(item) for item in data["dependency-groups"]["dev"])

    runtime_names = set(runtime)
    dev_names = set(dev)
    assert REQUIRED_RUNTIME <= runtime_names
    assert runtime_names <= (REQUIRED_RUNTIME | OPTIONAL)
    assert REQUIRED_DEV <= dev_names
    assert dev_names <= (REQUIRED_DEV | OPTIONAL)

    for pkg, expected_spec in VERSION_CONTRACT.items():
        assert runtime[pkg] == expected_spec, (pkg, runtime[pkg], expected_spec)

    lock = tomllib.loads((REPO_ROOT / "uv.lock").read_text(encoding="utf-8"))
    resolved: dict[str, str] = {}
    for package in lock["package"]:
        resolved[_normalize(package["name"])] = package["version"]
    for pkg in VERSION_CONTRACT:
        major = int(resolved[pkg].split(".")[0])
        assert major == 2, (pkg, resolved[pkg])


def test_prohibited_names_absent_from_pyproject_and_lock() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lock = tomllib.loads((REPO_ROOT / "uv.lock").read_text(encoding="utf-8"))
    lock_names = {_normalize(package["name"]) for package in lock["package"]}
    py_text_lower = pyproject.lower()
    for name in PROHIBITED:
        assert name not in lock_names
        assert name not in py_text_lower
    for name in lock_names:
        assert not name.startswith(_AZ + "-")
        assert name != _AZ
    assert (_AZ + "-") not in py_text_lower
    assert (_AZ + "_openai") not in py_text_lower
