"""A5 expected-tree oracle."""

from __future__ import annotations

import json
from fnmatch import fnmatch
from typing import Any, cast

from fath.tests.conftest import REPO_ROOT, candidate_paths


def _load_manifest() -> dict[str, Any]:
    path = REPO_ROOT / "src" / "fath" / "tests" / "fixtures" / "expected_tree.json"
    data: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return cast(dict[str, Any], data)


def _as_str_list(value: object) -> list[str]:
    assert isinstance(value, list)
    return [str(item) for item in value]


def _carved(paths: set[str]) -> set[str]:
    out: set[str] = set()
    for path in paths:
        if path == "docs" or path.startswith("docs/"):
            continue
        if path == ".delivery" or path.startswith(".delivery/"):
            continue
        out.add(path)
    return out


def posix_path_match(path: str, pattern: str) -> bool:
    """Match an anchored POSIX glob; '*' and '?' cannot cross '/'."""

    path_parts = path.split("/")
    pat_parts = pattern.split("/")
    if len(path_parts) != len(pat_parts):
        return False
    return all(fnmatch(seg, glob) for seg, glob in zip(path_parts, pat_parts, strict=True))


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(posix_path_match(path, pattern) for pattern in patterns)


def _nested_unauthorized_under(pattern: str) -> str:
    parent, name = pattern.rsplit("/", 1)
    if name.startswith("test_"):
        return f"{parent}/test_nested/unauthorized.py"
    if name == "0001_*.py":
        return f"{parent}/0001_nested/unauthorized.py"
    suffix = name[1:] if name.startswith("*") else name.split("*", 1)[-1]
    return f"{parent}/nested/unauthorized{suffix}"


def test_a5_rejects_nested_paths_under_single_level_globs() -> None:
    manifest = _load_manifest()
    required = _as_str_list(manifest["required"])
    permitted = _as_str_list(manifest["permitted"])
    allowed = required + permitted
    single_level = [p for p in permitted + required if "*" in p]
    assert single_level
    for pattern in single_level:
        nested = _nested_unauthorized_under(pattern)
        assert not _matches_any(nested, [pattern]), (pattern, nested)
        extras = [p for p in [nested] if not _matches_any(p, allowed)]
        assert extras == [nested], (pattern, nested, extras)


def test_a5_permits_immediate_children_of_single_level_globs() -> None:
    assert _matches_any(
        "src/fath/tests/unit/test_expected_tree.py",
        ["src/fath/tests/unit/test_*.py"],
    )
    assert _matches_any(
        "src/fath/tests/fixtures/expected_schema.json",
        ["src/fath/tests/fixtures/*.json"],
    )
    assert _matches_any(
        "src/fath/tests/fixtures/negative_migrations/N15_comment_separated_dml.py.sample",
        ["src/fath/tests/fixtures/negative_migrations/*.py.sample"],
    )


def test_expected_tree_conformance() -> None:
    manifest = _load_manifest()
    required = _as_str_list(manifest["required"])
    permitted = _as_str_list(manifest["permitted"])
    modules = set(_as_str_list(manifest["doc16_modules"]))
    domain = _carved(candidate_paths())

    required_ok: list[str] = []
    for entry in required:
        if "*" in entry:
            matches = sorted(p for p in domain if posix_path_match(p, entry))
            assert len(matches) == 1, (entry, matches)
            required_ok.append(entry)
        else:
            assert entry in domain, f"missing required path {entry}"
            required_ok.append(entry)

    allowed_patterns = required + permitted
    extras = [p for p in sorted(domain) if not _matches_any(p, allowed_patterns)]
    assert extras == [], extras

    for path in domain:
        if path.startswith("tests/") or path == "tests":
            raise AssertionError(f"prohibited top-level tests path: {path}")
        if path.startswith("migrations/") or path == "migrations":
            raise AssertionError(f"prohibited top-level migrations path: {path}")
        if path == "src/fath/config/sources_seed.yaml":
            raise AssertionError("prohibited sources_seed.yaml")
        if path.startswith("src/") and fnmatch(path, "*seed*"):
            raise AssertionError(f"prohibited seed path: {path}")
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "src" and parts[1] == "fath":
            first = parts[2]
            if first != "__init__.py" and first not in modules:
                raise AssertionError(f"noncanonical module path: {path}")

    version_py = [
        p
        for p in domain
        if p.startswith("src/fath/db/migrations/versions/")
        and p.endswith(".py")
        and not p.endswith("__init__.py")
    ]
    assert len(version_py) == 1, version_py
    assert posix_path_match(version_py[0], "src/fath/db/migrations/versions/0001_*.py")
