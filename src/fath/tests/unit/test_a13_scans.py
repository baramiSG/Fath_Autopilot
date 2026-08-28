"""A8/A9/A13 boundary scans, AMENDMENT-001, and secrets-hygiene scans."""

from __future__ import annotations

import ast
import json
import re
from fnmatch import fnmatch
from pathlib import Path
from urllib.parse import urlparse

from fath.tests.conftest import REPO_ROOT, candidate_paths

SCAN_INPUT = ".github/scan/authoritative_source_literals.json"
RFC2606_HOSTS = (
    "example.com",
    "example.net",
    "example.org",
    "test",
    "invalid",
)
WRITE_PATTERNS = re.compile(
    r"\bINSERT\b|\binsert\s*\(|\.add\s*\(|\bexecutemany\b|\bCOPY\b",
    re.IGNORECASE,
)
DB_IMPORT_MODULES = {"sqlalchemy", "asyncpg", "psycopg", "alembic"}
URL_RE = re.compile(r"https?://[^\s\"'`<>]+", re.IGNORECASE)
SLUG_VALUE_RE = re.compile(r"^synthetic_[a-z0-9_]+$")

_TOKEN_A = "A"
_TOKEN_HUNDRED = "100"
_TOKEN_AZURE = "azure"
_TOKEN_OPENAI = "openai"


def _a8_patterns() -> list[re.Pattern[str]]:
    return [
        re.compile(r"\b" + _TOKEN_A + _TOKEN_HUNDRED + r"\b", re.IGNORECASE),
        re.compile(_TOKEN_AZURE + r"\s+" + _TOKEN_OPENAI, re.IGNORECASE),
        re.compile(_TOKEN_AZURE + "-" + _TOKEN_OPENAI, re.IGNORECASE),
        re.compile(_TOKEN_AZURE + "_" + _TOKEN_OPENAI, re.IGNORECASE),
        re.compile("Azure" + "OpenAI"),
    ]


def _literals() -> list[str]:
    data = json.loads((REPO_ROOT / SCAN_INPUT).read_text(encoding="utf-8"))
    slugs = list(data["slugs"])
    names = list(data["display_names"])
    assert len(set(slugs)) == 39
    assert len(names) == 16
    return slugs + names


def _literal_regexes() -> list[re.Pattern[str]]:
    return [re.compile(r"\b" + re.escape(item) + r"\b", re.IGNORECASE) for item in _literals()]


def test_a13a_authoritative_literal_scan_is_clean() -> None:
    patterns = _literal_regexes()
    hits: list[str] = []
    for rel in sorted(candidate_paths()):
        if rel == SCAN_INPUT or rel.startswith("docs/") or rel.startswith(".delivery/"):
            continue
        path = REPO_ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern.search(text):
                hits.append(f"{rel}: {pattern.pattern}")
    assert hits == []


def test_a13b_i_no_registry_writes_outside_migrations_and_tests() -> None:
    hits: list[str] = []
    for rel in sorted(candidate_paths()):
        if not rel.startswith("src/"):
            continue
        if rel.startswith("src/fath/tests/") or rel.startswith("src/fath/db/migrations/"):
            continue
        path = REPO_ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "source_registry" in text and WRITE_PATTERNS.search(text):
            hits.append(rel)
    assert hits == []


def test_a13c_import_discipline() -> None:
    allowed_db_prefixes = (
        "src/fath/db/connection.py",
        "src/fath/db/migrations/",
        "src/fath/tests/",
    )
    hits: list[str] = []
    for rel in sorted(candidate_paths()):
        if not rel.startswith("src/fath/") or not rel.endswith(".py"):
            continue
        path = REPO_ROOT / rel
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        if imported & DB_IMPORT_MODULES:
            if not any(rel == p or rel.startswith(p) for p in allowed_db_prefixes):
                hits.append(rel)
        if rel.endswith("__init__.py"):
            body = [n for n in tree.body if not isinstance(n, ast.Expr)]
            exprs = [n for n in tree.body if isinstance(n, ast.Expr)]
            for expr in exprs:
                if not (isinstance(expr.value, ast.Constant) and isinstance(expr.value.value, str)):
                    hits.append(f"{rel}: non-docstring init body")
            if body:
                hits.append(f"{rel}: non-empty init")
    assert hits == []

    model = REPO_ROOT / "src/fath/db/models/source_registry.py"
    tree = ast.parse(model.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module.split(".")[0])
        for name in names:
            assert name in {
                "__future__",
                "datetime",
                "enum",
                "typing",
                "uuid",
                "pydantic",
            }, name


def test_a13d_fixture_syntheticity() -> None:
    patterns = _literal_regexes()
    fixture_root = REPO_ROOT / "src/fath/tests/fixtures"
    hits: list[str] = []
    for path in fixture_root.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern.search(text):
                hits.append(f"{path}: {pattern.pattern}")
        for url in URL_RE.findall(text):
            host = (urlparse(url).hostname or "").lower().rstrip(".")
            if not _rfc2606(host):
                hits.append(f"non-rfc2606 url {url} in {path}")
        if path.suffix in {".json", ".yaml", ".yml"}:
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = None
            if data is not None:
                _assert_slugs(data, path, hits)
    assert hits == []


def _rfc2606(host: str) -> bool:
    if host in RFC2606_HOSTS:
        return True
    return any(host == item or host.endswith("." + item) for item in RFC2606_HOSTS)


def _assert_slugs(data: object, path: Path, hits: list[str]) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"slug", "slugs"} and isinstance(value, str):
                if not SLUG_VALUE_RE.match(value):
                    hits.append(f"slug {value!r} in {path}")
            elif key in {"slug", "slugs"} and isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and not SLUG_VALUE_RE.match(item):
                        hits.append(f"slug {item!r} in {path}")
            else:
                _assert_slugs(value, path, hits)
    elif isinstance(data, list):
        for item in data:
            _assert_slugs(item, path, hits)


def test_no_seed_artifact_paths() -> None:
    paths = candidate_paths()
    assert "src/fath/config/sources_seed.yaml" not in paths
    seed_hits = [p for p in paths if p.startswith("src/") and fnmatch(p, "*seed*")]
    assert seed_hits == []


def test_a8_amendment_001_scan() -> None:
    targets = [
        "src",
        "docker",
        ".github",
        "pyproject.toml",
        "uv.lock",
        "docker-compose.yml",
        "Makefile",
        "alembic.ini",
        ".env.example",
    ]
    hits: list[str] = []
    files: list[Path] = []
    for target in targets:
        path = REPO_ROOT / target
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
    patterns = _a8_patterns()
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern.search(text):
                hits.append(f"{path.relative_to(REPO_ROOT)}: {pattern.pattern}")
    assert hits == []


def test_env_example_placeholders_only() -> None:
    text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    keys = []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, _, _value = line.partition("=")
        keys.append(key.strip())
    assert keys == ["DATABASE_URL", "REDIS_URL", "FATH_ENV"]


def test_env_is_gitignored() -> None:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert re.search(r"(?m)^\.env$", text)
    gitignore = REPO_ROOT / ".gitignore"
    env_file = REPO_ROOT / ".env"
    assert ".env" not in candidate_paths()
    assert gitignore.is_file()
    if env_file.exists():
        assert env_file.is_file()
