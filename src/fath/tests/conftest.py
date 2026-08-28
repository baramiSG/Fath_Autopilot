"""Shared test helpers (permitted conftest location)."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def candidate_paths() -> set[str]:
    """Tracked plus untracked non-ignored paths (pre-candidate equivalent of git ls-files)."""

    import subprocess

    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        text=True,
    ).split("\0")
    untracked = subprocess.check_output(
        ["git", "ls-files", "-o", "--exclude-standard", "-z"],
        cwd=REPO_ROOT,
        text=True,
    ).split("\0")
    return {p for p in tracked + untracked if p}


def sync_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        env_path = REPO_ROOT / ".env"
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("DATABASE_URL="):
                    url = line.split("=", 1)[1].strip()
                    break
    if not url:
        url = "postgresql+asyncpg://fath:fath@127.0.0.1:55432/fath"
    return url.replace("postgresql+asyncpg://", "postgresql://", 1).replace(
        "postgresql+psycopg://", "postgresql://", 1
    )


def redis_url() -> str:
    url = os.environ.get("REDIS_URL", "")
    if not url:
        env_path = REPO_ROOT / ".env"
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("REDIS_URL="):
                    url = line.split("=", 1)[1].strip()
                    break
    return url or "redis://127.0.0.1:56379/0"
