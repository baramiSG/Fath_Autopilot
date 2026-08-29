"""A13b-ii migration DML detector (plan §5 R1–R4 + IAC-001)."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from fath.tests.conftest import REPO_ROOT

MIGRATIONS_ROOT = REPO_ROOT / "src" / "fath" / "db" / "migrations"
VERSIONS_ROOT = MIGRATIONS_ROOT / "versions"
NEGATIVE_ROOT = REPO_ROOT / "src" / "fath" / "tests" / "fixtures" / "negative_migrations"

ALLOWED_OP_ATTRS = {
    "create_table",
    "drop_table",
    "create_index",
    "drop_index",
    "create_check_constraint",
    "drop_constraint",
    "execute",
}
PROHIBITED_NAMES = {
    "insert",
    "update",
    "delete",
    "bulk_insert",
    "executemany",
    "exec_driver_sql",
    "get_bind",
    "merge",
    "copy_expert",
    "copy_from",
}
DYNAMIC_NAMES = {
    "getattr",
    "setattr",
    "eval",
    "exec",
    "__import__",
    "globals",
    "locals",
    "vars",
    "attrgetter",
    "itemgetter",
    "methodcaller",
}
SINK_ATTRS = {
    "execute",
    "executemany",
    "exec_driver_sql",
    "scalar",
    "scalars",
    "stream",
}
ALIASABLE_ATTRS = SINK_ATTRS | ALLOWED_OP_ATTRS | PROHIBITED_NAMES
DDL_PREFIX = re.compile(r"^\s*(CREATE|DROP|ALTER|COMMENT)\b", re.IGNORECASE)
DDL_STATEMENT_HEADS = frozenset({"CREATE", "DROP", "ALTER", "COMMENT"})
DOLLAR_TAG = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$")
LEADING_WORD = re.compile(r"[A-Za-z_]+")
DML_IN_STRING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+\w+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b|"
    r"\bCOPY\s+\w+\s+FROM\b|\bMERGE\s+INTO\b",
    re.IGNORECASE,
)
DYNAMIC_EXECUTE = re.compile(
    r"\bEXECUTE\b(?!\s+(FUNCTION|PROCEDURE)\b)",
    re.IGNORECASE,
)
SQL_LITERAL_CHAIN = re.compile(
    r"'[^']*'(?:\s*(?:\|\|)?\s*'[^']*')+",
)
EXPECTED_NEGATIVE = {
    "N1_sa_insert_delete.py.sample",
    "N2_bulk_insert.py.sample",
    "N3_execute_insert_string.py.sample",
    "N4_get_bind.py.sample",
    "N5_table_insert.py.sample",
    "N6_ddl_prefix_then_dml.py.sample",
    "N7_getattr_indirection.py.sample",
    "N8_aliased_imports.py.sample",
    "N9_assembled_sql.py.sample",
    "N10_import_alembic_op_alias.py.sample",
    "N11_execute_callable_alias.py.sample",
    "N12_attrgetter_execute.py.sample",
    "N13_replace_assembled_dml.py.sample",
    "N14_env_connection_execute.py.sample",
    "N15_comment_separated_dml.py.sample",
    "N16_plpgsql_dynamic_dml.py.sample",
    "N17_qualified_copy_from_program.py.sample",
    "N18_update_only_set.py.sample",
}

REVIEWER_BYPASS_PROBES: list[tuple[str, str, bool]] = [
    (
        "import alembic.op as o2",
        """
import alembic.op as o2
def upgrade() -> None:
    o2.execute("XNSERT INTO synthetic_t VALUES (1)".replace("X", "I"))
""",
        True,
    ),
    (
        "run = op.execute",
        """
from alembic import op
def upgrade() -> None:
    run = op.execute
    run("XNSERT INTO synthetic_t VALUES (1)".replace("X", "I"))
""",
        True,
    ),
    (
        "operator.attrgetter execute",
        """
import operator
from alembic import op
def upgrade() -> None:
    operator.attrgetter("execute")(op)("XNSERT INTO synthetic_t VALUES (1)".replace("X", "I"))
""",
        True,
    ),
    (
        "replace-assembled DML via aliased sink",
        """
from alembic import op
def upgrade() -> None:
    sql = "XNSERT INTO synthetic_t VALUES (1)".replace("X", "I")
    helper = op.execute
    helper(sql)
""",
        True,
    ),
    (
        "connection.execute in env.py",
        """
from alembic import context
from sqlalchemy import engine_from_config, pool
def run_migrations_online() -> None:
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        connection.execute("XNSERT INTO synthetic_t VALUES (1)".replace("X", "I"))
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
""",
        False,
    ),
]

SQL_TOKEN_EVASION_PROBES: list[tuple[str, str]] = [
    (
        "comment-separated INSERT/**/INTO and DELETE/**/FROM",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_comment_dml (id int);
        INSERT/**/INTO synthetic_comment_dml VALUES (1);
        DELETE/**/FROM synthetic_comment_dml;
    """)
''',
    ),
    (
        "spaced SQL comments between DML keywords",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_comment_dml (id int);
        INSERT /* c */ INTO synthetic_comment_dml VALUES (1);
        DELETE /* c */ FROM synthetic_comment_dml;
    """)
''',
    ),
    (
        "line-comment split DML keywords",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_comment_dml (id int);
        INSERT -- x
        INTO synthetic_comment_dml VALUES (1);
        DELETE -- y
        FROM synthetic_comment_dml;
    """)
''',
    ),
    (
        "PL/pgSQL EXECUTE of concatenated DML literals",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION synthetic_dyn_dml() RETURNS void
        LANGUAGE plpgsql
        AS $fn$
        BEGIN
            EXECUTE 'INSERT' || ' INTO synthetic_dyn_dml_t VALUES (1)';
            EXECUTE 'DELETE' || ' FROM synthetic_dyn_dml_t';
        END;
        $fn$;
    """)
''',
    ),
    (
        "PL/pgSQL EXECUTE of variable-assembled DML",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION synthetic_dyn_dml() RETURNS void
        LANGUAGE plpgsql
        AS $fn$
        DECLARE
            verb text := 'INSERT';
            stmt text;
        BEGIN
            stmt := verb || ' INTO synthetic_dyn_dml_t VALUES (1)';
            EXECUTE stmt;
        END;
        $fn$;
    """)
''',
    ),
]

STATEMENT_ALLOWLIST_PROBES: list[tuple[str, str]] = [
    (
        "schema-qualified COPY ... (cols) FROM PROGRAM after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_copy_probe (id int, label text);
        COPY public.synthetic_copy_probe (id, label) FROM PROGRAM 'echo synthetic';
    """)
''',
    ),
    (
        "quoted-identifier COPY ... (cols) FROM PROGRAM after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_copy_probe (id int, label text);
        COPY "public"."synthetic_copy_probe" (id, label) FROM PROGRAM 'echo synthetic';
    """)
''',
    ),
    (
        "COPY ... FROM STDIN (bare and qualified) after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_copy_probe (id int);
        COPY synthetic_copy_probe FROM STDIN;
    """)
''',
    ),
    (
        "UPDATE ONLY qualified-table SET after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_update_probe (id int, label text);
        UPDATE ONLY public.synthetic_update_probe SET label = 'x' WHERE id = 1;
    """)
''',
    ),
    (
        "savepoint / rollback-to-savepoint transaction-control concealment",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_probe (id int);
        SAVEPOINT synthetic_sp;
        COPY public.synthetic_probe (id) FROM PROGRAM 'echo 1';
        ROLLBACK TO SAVEPOINT synthetic_sp;
        RELEASE SAVEPOINT synthetic_sp;
    """)
''',
    ),
    (
        "quoted-identifier INSERT after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_probe (id int);
        INSERT INTO "public"."synthetic_probe" (id) VALUES (1);
    """)
''',
    ),
    (
        "CTE-fronted INSERT (WITH ... INSERT) after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_probe (id int);
        WITH s AS (SELECT 1 AS id) INSERT INTO synthetic_probe (id) SELECT id FROM s;
    """)
''',
    ),
    (
        "MERGE INTO qualified target after a DDL prefix",
        '''
from alembic import op
def upgrade() -> None:
    op.execute("""
        CREATE TABLE synthetic_probe (id int);
        MERGE INTO public.synthetic_probe t USING (SELECT 1 AS id) s
            ON t.id = s.id WHEN NOT MATCHED THEN INSERT (id) VALUES (s.id);
    """)
''',
    ),
]


def _identifier(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_os_path_join(func: ast.Attribute) -> bool:
    value = func.value
    return (
        isinstance(value, ast.Attribute)
        and value.attr == "path"
        and isinstance(value.value, ast.Name)
        and value.value.id == "os"
    )


def _is_canonical_op_import(node: ast.ImportFrom) -> bool:
    return (
        node.module == "alembic"
        and (node.level or 0) == 0
        and len(node.names) == 1
        and node.names[0].name == "op"
        and node.names[0].asname in (None, "op")
    )


def _is_canonical_sa_import(node: ast.Import) -> bool:
    return (
        len(node.names) == 1 and node.names[0].name == "sqlalchemy" and node.names[0].asname == "sa"
    )


def _is_allowed_env_import(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return len(node.names) == 1 and node.names[0].name == "os" and node.names[0].asname is None
    if isinstance(node, ast.ImportFrom):
        if (node.module or "") == "logging.config":
            return (
                (node.level or 0) == 0
                and len(node.names) == 1
                and node.names[0].name == "fileConfig"
                and node.names[0].asname is None
            )
        if (node.module or "") == "alembic":
            return (
                (node.level or 0) == 0
                and len(node.names) == 1
                and node.names[0].name == "context"
                and node.names[0].asname is None
            )
        if (node.module or "") == "sqlalchemy":
            names = {alias.name for alias in node.names}
            return (
                (node.level or 0) == 0
                and names <= {"engine_from_config", "pool"}
                and bool(names)
                and all(alias.asname is None for alias in node.names)
            )
    return False


def _is_allowed_version_import(node: ast.AST) -> bool:
    if isinstance(node, ast.ImportFrom) and _is_canonical_op_import(node):
        return True
    if isinstance(node, ast.Import) and _is_canonical_sa_import(node):
        return True
    return False


def _is_allowed_op_execute_func(func: ast.AST) -> bool:
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "execute"
        and isinstance(func.value, ast.Name)
        and func.value.id == "op"
    )


def _assignment_value(node: ast.AST) -> ast.AST | None:
    if isinstance(node, ast.Assign):
        return node.value
    if isinstance(node, ast.AnnAssign):
        return node.value
    if isinstance(node, ast.NamedExpr):
        return node.value
    return None


def _aliased_execution_attrs(value: ast.AST) -> list[str]:
    found: list[str] = []
    if isinstance(value, ast.Attribute) and value.attr in ALIASABLE_ATTRS:
        found.append(value.attr)
    if isinstance(value, ast.Name) and value.id in {"op", "sa"}:
        found.append(value.id)
    if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        for elt in value.elts:
            found.extend(_aliased_execution_attrs(elt))
    return found


def _version_call_allowed(func: ast.AST) -> bool:
    if not isinstance(func, ast.Attribute):
        return False
    if not isinstance(func.value, ast.Name):
        return False
    if func.value.id == "op":
        return func.attr in ALLOWED_OP_ATTRS
    if func.value.id == "sa":
        return func.attr not in PROHIBITED_NAMES and func.attr not in SINK_ATTRS
    return False


def normalize_sql_comments(sql: str) -> str:
    """Replace SQL comments with a space; preserve quoted strings and identifiers."""

    out: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        if ch == "'":
            out.append("'")
            i += 1
            while i < n:
                if sql[i] == "'" and i + 1 < n and sql[i + 1] == "'":
                    out.append("''")
                    i += 2
                    continue
                out.append(sql[i])
                if sql[i] == "'":
                    i += 1
                    break
                i += 1
            continue
        if ch == '"':
            out.append('"')
            i += 1
            while i < n:
                if sql[i] == '"' and i + 1 < n and sql[i + 1] == '"':
                    out.append('""')
                    i += 2
                    continue
                out.append(sql[i])
                if sql[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if sql.startswith("--", i):
            out.append(" ")
            i += 2
            while i < n and sql[i] != "\n":
                i += 1
            continue
        if sql.startswith("/*", i):
            depth = 1
            i += 2
            while i < n and depth:
                if sql.startswith("/*", i):
                    depth += 1
                    i += 2
                elif sql.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            out.append(" ")
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _sql_string_literal_contents(sql: str) -> list[str]:
    contents: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        if sql[i] == "'":
            i += 1
            buf: list[str] = []
            while i < n:
                if sql[i] == "'" and i + 1 < n and sql[i + 1] == "'":
                    buf.append("'")
                    i += 2
                    continue
                if sql[i] == "'":
                    i += 1
                    break
                buf.append(sql[i])
                i += 1
            contents.append("".join(buf))
            continue
        if sql[i] == '"':
            i += 1
            while i < n:
                if sql[i] == '"' and i + 1 < n and sql[i + 1] == '"':
                    i += 2
                    continue
                if sql[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        i += 1
    return contents


def _blank_sql_strings(sql: str) -> str:
    out: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        if sql[i] == "'":
            i += 1
            out.append(" ")
            while i < n:
                if sql[i] == "'" and i + 1 < n and sql[i + 1] == "'":
                    i += 2
                    continue
                if sql[i] == "'":
                    i += 1
                    break
                i += 1
            continue
        if sql[i] == '"':
            i += 1
            out.append(" ")
            while i < n:
                if sql[i] == '"' and i + 1 < n and sql[i + 1] == '"':
                    i += 2
                    continue
                if sql[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        out.append(sql[i])
        i += 1
    return "".join(out)


def _collapsed_sql_literal_chains(sql: str) -> list[str]:
    collapsed: list[str] = []
    for match in SQL_LITERAL_CHAIN.finditer(sql):
        collapsed.append("".join(re.findall(r"'([^']*)'", match.group(0))))
    return collapsed


def sql_string_contains_dml(sql: str) -> list[str]:
    """Return violation messages for DML or dynamic EXECUTE in a SQL string."""

    messages: list[str] = []
    normalized = normalize_sql_comments(sql)
    if DML_IN_STRING.search(normalized):
        messages.append("string literal contains DML keyword form")
    for literal in _sql_string_literal_contents(normalized):
        inner = normalize_sql_comments(literal)
        if DML_IN_STRING.search(inner):
            messages.append("string literal contains DML keyword form")
    for chain in _collapsed_sql_literal_chains(normalized):
        inner = normalize_sql_comments(chain)
        if DML_IN_STRING.search(inner):
            messages.append("string literal contains assembled DML keyword form")
    if DYNAMIC_EXECUTE.search(_blank_sql_strings(normalized)):
        messages.append("string literal contains dynamic SQL EXECUTE")
    return messages


def _split_top_level_sql_statements(sql: str) -> list[str]:
    """Split SQL on top-level ``;``, respecting quotes, dollar-quotes, and comments.

    Semicolons inside single-quoted strings, double-quoted identifiers,
    dollar-quoted bodies (e.g. PL/pgSQL ``$fn$ … END; $fn$``), line comments and
    (nestable) block comments are NOT statement separators.
    """

    statements: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        if sql.startswith("--", i):
            buf.append(sql[i])
            i += 1
            while i < n and sql[i] != "\n":
                buf.append(sql[i])
                i += 1
            continue
        if sql.startswith("/*", i):
            depth = 1
            buf.append("/*")
            i += 2
            while i < n and depth:
                if sql.startswith("/*", i):
                    depth += 1
                    buf.append("/*")
                    i += 2
                elif sql.startswith("*/", i):
                    depth -= 1
                    buf.append("*/")
                    i += 2
                else:
                    buf.append(sql[i])
                    i += 1
            continue
        if ch == "'":
            buf.append(ch)
            i += 1
            while i < n:
                if sql[i] == "'" and i + 1 < n and sql[i + 1] == "'":
                    buf.append("''")
                    i += 2
                    continue
                buf.append(sql[i])
                if sql[i] == "'":
                    i += 1
                    break
                i += 1
            continue
        if ch == '"':
            buf.append(ch)
            i += 1
            while i < n:
                if sql[i] == '"' and i + 1 < n and sql[i + 1] == '"':
                    buf.append('""')
                    i += 2
                    continue
                buf.append(sql[i])
                if sql[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        tag_match = DOLLAR_TAG.match(sql, i)
        if tag_match is not None:
            tag = tag_match.group(0)
            buf.append(tag)
            i += len(tag)
            end = sql.find(tag, i)
            if end == -1:
                buf.append(sql[i:])
                i = n
            else:
                buf.append(sql[i:end])
                buf.append(tag)
                i = end + len(tag)
            continue
        if ch == ";":
            statements.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        statements.append("".join(buf))
    return statements


def _statement_head(statement: str) -> str | None:
    """First keyword token of a statement, skipping leading whitespace and comments."""

    i = 0
    n = len(statement)
    while i < n:
        ch = statement[i]
        if ch.isspace():
            i += 1
            continue
        if statement.startswith("--", i):
            i += 2
            while i < n and statement[i] != "\n":
                i += 1
            continue
        if statement.startswith("/*", i):
            depth = 1
            i += 2
            while i < n and depth:
                if statement.startswith("/*", i):
                    depth += 1
                    i += 2
                elif statement.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            continue
        break
    word = LEADING_WORD.match(statement, i)
    return word.group(0).upper() if word else None


def sql_executed_statements_all_ddl(sql: str) -> list[str]:
    """Conservative allowlist: every executed migration statement must be DDL.

    Splits the SQL into top-level statements and requires each non-empty statement
    to begin with an allowlisted DDL head (CREATE / DROP / ALTER / COMMENT — the
    plan §5 R2 keyword set). This rejects the whole non-DDL class by construction:
    ``COPY`` in any qualified/quoted/column-list/``FROM PROGRAM``/``FROM STDIN``
    form, ``UPDATE ONLY``, ``INSERT``, ``WITH … INSERT``, ``DELETE``, ``TRUNCATE``,
    ``MERGE``, and transaction-control concealment (``SAVEPOINT`` / ``ROLLBACK TO``
    / ``RELEASE`` / ``BEGIN`` / ``COMMIT`` / ``START``), while accepting the
    legitimate DDL corpus including PL/pgSQL dollar-quoted function bodies.
    """

    messages: list[str] = []
    for statement in _split_top_level_sql_statements(sql):
        head = _statement_head(statement)
        if head is None:
            continue
        if head not in DDL_STATEMENT_HEADS:
            messages.append(f"non-DDL statement head {head!r} in executed migration SQL")
    return messages


def check_source(source: str, *, is_version_script: bool) -> list[str]:
    """Return violation messages; empty list means the file passes."""

    violations: list[str] = []
    tree = ast.parse(source)

    allowed_sink_attrs: set[int] = set()
    if is_version_script:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_allowed_op_execute_func(node.func):
                allowed_sink_attrs.add(id(node.func))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if is_version_script:
                if not _is_allowed_version_import(node):
                    violations.append("noncanonical import in version script")
            elif not _is_allowed_env_import(node):
                violations.append("noncanonical import in migration file")

        ident = _identifier(node)
        if ident in DYNAMIC_NAMES:
            violations.append(f"dynamic dispatch identifier {ident!r}")
        if ident in PROHIBITED_NAMES:
            violations.append(f"prohibited name {ident!r}")

        if isinstance(node, ast.JoinedStr):
            violations.append("f-string assembly is prohibited in migration files")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            violations.append("string/value concatenation is prohibited in migration files")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            violations.append("% string formatting is prohibited in migration files")

        rhs = _assignment_value(node)
        if rhs is not None:
            for attr in _aliased_execution_attrs(rhs):
                violations.append(f"callable alias of {attr!r} is prohibited")

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "format":
                violations.append("string assembly via .format is prohibited")
            if isinstance(func, ast.Attribute) and func.attr == "join":
                if not _is_os_path_join(func):
                    violations.append("string assembly via str.join is prohibited")
            if isinstance(func, ast.Name) and func.id == "join":
                violations.append("str.join assembly is prohibited")
            if isinstance(func, ast.Attribute) and func.attr == "replace":
                if is_version_script or isinstance(func.value, ast.Constant):
                    violations.append("string assembly via .replace is prohibited")
            if isinstance(func, ast.Attribute) and func.attr in SINK_ATTRS:
                if id(func) not in allowed_sink_attrs:
                    violations.append(f"unrecognised execution sink {func.attr!r}")
            if is_version_script and not _version_call_allowed(func):
                violations.append("unrecognised call in version script")
            if is_version_script and _is_allowed_op_execute_func(func):
                if len(node.args) != 1 or node.keywords:
                    violations.append("op.execute must take exactly one positional argument")
                else:
                    arg = node.args[0]
                    if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                        violations.append("op.execute argument is not a plain string literal")
                    else:
                        if not DDL_PREFIX.match(arg.value):
                            violations.append("op.execute string does not begin with a DDL keyword")
                        violations.extend(sql_executed_statements_all_ddl(arg.value))

        if isinstance(node, ast.Attribute) and node.attr in SINK_ATTRS:
            if id(node) not in allowed_sink_attrs:
                violations.append(f"execution attribute {node.attr!r} is not an allowed sink")

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            messages = sql_string_contains_dml(node.value)
            if messages:
                violations.extend(messages)

    return violations


def check_path(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    is_version = path.parent.resolve() == VERSIONS_ROOT.resolve() and path.suffix == ".py"
    return check_source(source, is_version_script=is_version)


def _real_migration_py_files() -> list[Path]:
    return sorted(p for p in MIGRATIONS_ROOT.rglob("*.py") if p.is_file())


def test_every_real_migration_file_passes() -> None:
    files = _real_migration_py_files()
    assert files, "no migration python files found"
    failures: dict[str, list[str]] = {}
    for path in files:
        msgs = check_path(path)
        if msgs:
            failures[str(path.relative_to(REPO_ROOT))] = msgs
    assert failures == {}


def test_every_negative_fixture_n1_through_n18_fails() -> None:
    names = sorted(p.name for p in NEGATIVE_ROOT.glob("*.py.sample"))
    assert set(names) >= EXPECTED_NEGATIVE
    for name in sorted(EXPECTED_NEGATIVE):
        path = NEGATIVE_ROOT / name
        source = path.read_text(encoding="utf-8")
        is_version = not name.startswith("N14_")
        msgs = check_source(source, is_version_script=is_version)
        assert msgs, f"{name} was expected to fail the DML detector but passed"


def test_statement_allowlist_probes_are_rejected() -> None:
    for name, source in STATEMENT_ALLOWLIST_PROBES:
        msgs = check_source(source, is_version_script=True)
        assert msgs, f"statement-allowlist probe {name!r} was expected to fail but passed"


def test_r4_regex_misses_impl008_forms_allowlist_still_rejects() -> None:
    """Load-bearing allowlist: plan R4 regex does not match the demonstrated forms."""

    copy_sql = (
        "CREATE TABLE synthetic_copy_probe (id int, label text);\n"
        "COPY public.synthetic_copy_probe (id, label) FROM PROGRAM 'echo synthetic';\n"
    )
    quoted_copy_sql = (
        "CREATE TABLE synthetic_copy_probe (id int, label text);\n"
        'COPY "public"."synthetic_copy_probe" (id, label) '
        "FROM PROGRAM 'echo synthetic';\n"
    )
    update_sql = (
        "CREATE TABLE synthetic_update_probe (id int, label text);\n"
        "UPDATE ONLY public.synthetic_update_probe SET label = 'x' WHERE id = 1;\n"
    )
    assert DML_IN_STRING.search(normalize_sql_comments(copy_sql)) is None
    assert DML_IN_STRING.search(normalize_sql_comments(quoted_copy_sql)) is None
    assert DML_IN_STRING.search(normalize_sql_comments(update_sql)) is None
    assert sql_string_contains_dml(copy_sql) == []
    assert sql_string_contains_dml(quoted_copy_sql) == []
    assert sql_string_contains_dml(update_sql) == []
    assert sql_executed_statements_all_ddl(copy_sql)
    assert sql_executed_statements_all_ddl(quoted_copy_sql)
    assert sql_executed_statements_all_ddl(update_sql)


def test_reviewer_bypass_probes_are_rejected() -> None:
    for name, source, is_version in REVIEWER_BYPASS_PROBES:
        msgs = check_source(source, is_version_script=is_version)
        assert msgs, f"bypass probe {name!r} was expected to fail the DML detector but passed"


def test_sql_token_evasion_probes_are_rejected() -> None:
    for name, source in SQL_TOKEN_EVASION_PROBES:
        msgs = check_source(source, is_version_script=True)
        assert msgs, f"SQL token evasion {name!r} was expected to fail the DML detector but passed"


def test_legitimate_ddl_corpus_passes() -> None:
    source = '''
from alembic import op

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE FUNCTION fath_source_id_immutable()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $fn$
        BEGIN
            IF NEW.source_id IS DISTINCT FROM OLD.source_id THEN
                RAISE EXCEPTION 'source_id is immutable';
            END IF;
            RETURN NEW;
        END;
        $fn$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_source_registry_source_id_immutable
        BEFORE UPDATE ON source_registry
        FOR EACH ROW
        EXECUTE FUNCTION fath_source_id_immutable()
        """
    )
    op.execute(
        """
        CREATE FUNCTION fath_audit_log_append_only()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $fn$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only';
        END;
        $fn$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION fath_audit_log_append_only()
        """
    )
'''
    assert check_source(source, is_version_script=True) == []


def test_negative_fixture_files_are_not_collected_as_python() -> None:
    for path in NEGATIVE_ROOT.glob("*.py.sample"):
        assert path.suffix == ".sample"
    assert not list(NEGATIVE_ROOT.glob("*.py"))
