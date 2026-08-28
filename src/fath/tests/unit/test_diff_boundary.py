"""A16 working-tree boundary check against the governed base SHA."""

from __future__ import annotations

import re
import subprocess

from fath.tests.conftest import REPO_ROOT, candidate_paths

BASE_PATH = REPO_ROOT / ".delivery" / "evidence" / "TASK-001" / "BASE_SHA.txt"


def test_base_sha_file_matches_governed_identity() -> None:
    text = BASE_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) == 1
    assert re.fullmatch(r"[0-9a-f]{40}", lines[0])
    assert lines[0] == "2649fb91b73c1d352bcd59a96cc9bf2e3dee27a9"


def test_a16_working_tree_boundary() -> None:
    base = BASE_PATH.read_text(encoding="utf-8").strip()
    subprocess.check_call(["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=REPO_ROOT)
    diff = subprocess.check_output(
        ["git", "diff", "--name-status", "--no-renames", base],
        cwd=REPO_ROOT,
        text=True,
    )
    entries: list[tuple[str, str]] = []
    for line in diff.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        entries.append((status, path))
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
    )
    for path in sorted(candidate_paths()):
        if path not in tracked:
            entries.append(("A", path))

    failures: list[str] = []
    for status, path in entries:
        if path == "docs" or path.startswith("docs/"):
            failures.append(f"{status} {path}")
        if path == ".delivery" or path.startswith(".delivery/"):
            if status != "A" or not path.startswith(".delivery/evidence/TASK-001/"):
                failures.append(f"{status} {path}")
    assert failures == []
