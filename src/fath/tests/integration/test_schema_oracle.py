"""A4 schema oracle and A4 negative constraint/trigger tests."""

from __future__ import annotations

import json
import re
from typing import Any

import psycopg
import pytest

from fath.tests.conftest import REPO_ROOT, sync_database_url

pytestmark = pytest.mark.integration

INSERT_SQL = """
INSERT INTO public.source_registry (
    slug, name, source_class, reliability_tier, base_url, access_method,
    auth_requirement, allowed_paths, disallowed_paths, robots_status,
    max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
    language_codes, country_scope, topic_scope, update_frequency_hint,
    reliability_prior, strategic_relevance_score, enabled,
    created_at, updated_at, metadata
) VALUES (
    %s, 'Synthetic Row', 'global_indicator', 'institutional',
    'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
    30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
    0.7, 0.5, true, now(), now(), '{}'::jsonb
)
"""


def _connect() -> psycopg.Connection[Any]:
    return psycopg.connect(sync_database_url())


def _norm_ws(value: str) -> str:
    return " ".join(value.split())


def _norm_type(fmt: str) -> str:
    mapping = {
        "timestamp with time zone": "timestamptz",
        "boolean": "boolean",
        "integer": "integer",
        "bigint": "bigint",
        "double precision": "double precision",
        "jsonb": "jsonb",
        "uuid": "uuid",
        "text": "text",
        "text[]": "text[]",
    }
    return mapping.get(fmt, fmt)


def _normalize_check_def(definition: str) -> str:
    compact = re.sub(r"::\w+(?:\s+\w+)*", "", _norm_ws(definition))
    compact = re.sub(r"\((\d+(?:\.\d+)?)\)", r"\1", compact)
    return compact


def _expected_numeric_check(column: str, ge: int | float, le: int | float | None) -> str:
    if le is None:
        return f"CHECK (({column} >= {ge}))"
    return f"CHECK ((({column} >= {ge}) AND ({column} <= {le})))"


def _split_top_level_sql_list(body: str) -> list[str]:
    if not body.strip():
        return []
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    in_str = False
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if in_str:
            buf.append(ch)
            if ch == "'":
                if i + 1 < n and body[i + 1] == "'":
                    buf.append("'")
                    i += 2
                    continue
                in_str = False
            i += 1
            continue
        if ch == "'":
            in_str = True
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return parts


def _quoted_sql_literal(element: str) -> str | None:
    match = re.fullmatch(r"'([^']*)'", element.strip())
    if match is None:
        return None
    return match.group(1)


def assert_constraint_semantics(
    expected: dict[str, Any],
    contype: str,
    definition: str,
    columns: list[str],
) -> None:
    """Compare one live constraint to the pre-bound expected semantics."""

    assert contype == expected["contype"]
    assert columns == expected["columns"]
    if contype in {"p", "u"}:
        return
    if "values" in expected:
        norm = _normalize_check_def(definition)
        assert " AND " not in norm, norm
        assert " OR " not in norm, norm
        column = expected["columns"][0]
        match = re.fullmatch(
            rf"CHECK \(\({re.escape(column)} = ANY \(ARRAY\[(.*)\]\)\)\)",
            norm,
        )
        assert match is not None, norm
        literals: list[str] = []
        for raw in _split_top_level_sql_list(match.group(1)):
            value = _quoted_sql_literal(raw)
            assert value is not None, f"non-constant enum array element: {raw!r}"
            literals.append(value)
        assert set(literals) == set(expected["values"])
        return
    numeric = expected["numeric"]
    assert columns == [numeric["column"]]
    expected_def = _expected_numeric_check(
        numeric["column"],
        numeric["ge"],
        numeric.get("le"),
    )
    assert _normalize_check_def(definition) == expected_def


@pytest.fixture()
def conn() -> Any:
    connection = _connect()
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


def test_a4_expected_schema(conn: Any) -> None:
    expected = json.loads(
        (REPO_ROOT / "src/fath/tests/fixtures/expected_schema.json").read_text(encoding="utf-8")
    )
    tables = {
        row[0]
        for row in conn.execute(
            """
            SELECT relname FROM pg_class
            WHERE relnamespace = 'public'::regnamespace AND relkind = 'r'
            """
        )
    }
    assert tables == set(expected["table_set"])

    sources_exists = conn.execute(
        "SELECT COUNT(*) FROM pg_class WHERE relname = 'sources' AND relkind = 'r'"
    ).fetchone()
    assert sources_exists is not None and sources_exists[0] == 0

    fk_count = conn.execute(
        """
        SELECT count(*) FROM pg_constraint
        WHERE contype = 'f' AND connamespace = 'public'::regnamespace
        """
    ).fetchone()
    assert fk_count is not None and fk_count[0] == expected["fk_count_public"]

    slug_fk = conn.execute(
        """
        SELECT count(*) FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
        JOIN pg_class t ON t.oid = c.confrelid
        WHERE c.contype = 'f' AND t.relname = 'source_registry' AND a.attname = 'slug'
        """
    ).fetchone()
    assert slug_fk is not None and slug_fk[0] == 0

    columns = list(
        conn.execute(
            """
            SELECT a.attname,
                   pg_catalog.format_type(a.atttypid, a.atttypmod),
                   a.attnotnull,
                   pg_get_expr(ad.adbin, ad.adrelid)
            FROM pg_attribute a
            LEFT JOIN pg_attrdef ad ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
            WHERE a.attrelid = 'public.source_registry'::regclass
              AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
            """
        )
    )
    live = [
        {
            "name": name,
            "type": _norm_type(fmt),
            "not_null": notnull,
            "default": None if default is None else _norm_ws(default),
        }
        for name, fmt, notnull, default in columns
    ]
    assert live == expected["columns"]

    constraints = list(
        conn.execute(
            """
            SELECT conname, contype, pg_get_constraintdef(oid), conkey
            FROM pg_constraint
            WHERE conrelid = 'public.source_registry'::regclass
            ORDER BY conname
            """
        )
    )
    assert {row[0] for row in constraints} == {c["name"] for c in expected["constraints"]}
    assert len(constraints) == 13

    attnames = {
        row[0]: row[1]
        for row in conn.execute(
            """
            SELECT attnum, attname FROM pg_attribute
            WHERE attrelid = 'public.source_registry'::regclass AND attnum > 0
            """
        )
    }
    expected_by_name = {c["name"]: c for c in expected["constraints"]}
    for name, contype, definition, conkey in constraints:
        exp = expected_by_name[name]
        cols = [attnames[int(n)] for n in conkey]
        assert_constraint_semantics(exp, contype, definition, cols)

    indexdefs = [
        _norm_ws(row[0])
        for row in conn.execute(
            """
            SELECT pg_get_indexdef(i.indexrelid)
            FROM pg_index i
            WHERE i.indrelid = 'public.source_registry'::regclass
            ORDER BY pg_get_indexdef(i.indexrelid)
            """
        )
    ]
    expected_indexes = sorted(_norm_ws(s) for s in expected["indexes"])
    assert indexdefs == expected_indexes

    triggers = list(
        conn.execute(
            """
            SELECT t.tgname, p.proname, t.tgtype, t.tgenabled
            FROM pg_trigger t
            JOIN pg_proc p ON p.oid = t.tgfoid
            WHERE t.tgrelid = 'public.source_registry'::regclass AND NOT t.tgisinternal
            """
        )
    )
    assert len(triggers) == 1
    name, function, tgtype, enabled = triggers[0]
    assert name == expected["trigger"]["name"]
    assert function == expected["trigger"]["function"]
    assert enabled != "D"
    assert tgtype & 2  # BEFORE
    assert tgtype & 16  # UPDATE
    assert tgtype & 1  # ROW

    exts = {row[0] for row in conn.execute("SELECT extname FROM pg_extension")}
    assert set(expected["extensions"]) <= exts


def test_negative_bogus_status(conn: Any) -> None:
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            """
            INSERT INTO public.source_registry (
                slug, name, source_class, reliability_tier, base_url, access_method,
                auth_requirement, allowed_paths, disallowed_paths, robots_status,
                max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
                language_codes, country_scope, topic_scope, update_frequency_hint,
                reliability_prior, strategic_relevance_score, enabled,
                created_at, updated_at, metadata, status
            ) VALUES (
                'synthetic_bogus_status', 'Synthetic Row', 'global_indicator', 'institutional',
                'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
                30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
                0.7, 0.5, true, now(), now(), '{}'::jsonb, 'bogus'
            )
            """
        )
    conn.rollback()


def test_negative_null_slug(conn: Any) -> None:
    with pytest.raises(psycopg.errors.NotNullViolation):
        conn.execute(INSERT_SQL, (None,))
    conn.rollback()


def test_negative_duplicate_slug(conn: Any) -> None:
    conn.execute(INSERT_SQL, ("synthetic_dup_slug",))
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(INSERT_SQL, ("synthetic_dup_slug",))
    conn.rollback()


def test_negative_duplicate_source_id(conn: Any) -> None:
    row = conn.execute(
        INSERT_SQL + " RETURNING source_id",
        ("synthetic_dup_id_a",),
    ).fetchone()
    assert row is not None
    source_id = row[0]
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(
            """
            INSERT INTO public.source_registry (
                source_id, slug, name, source_class, reliability_tier, base_url, access_method,
                auth_requirement, allowed_paths, disallowed_paths, robots_status,
                max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
                language_codes, country_scope, topic_scope, update_frequency_hint,
                reliability_prior, strategic_relevance_score, enabled,
                created_at, updated_at, metadata
            ) VALUES (
                %s, 'synthetic_dup_id_b', 'Synthetic Row', 'global_indicator', 'institutional',
                'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
                30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
                0.7, 0.5, true, now(), now(), '{}'::jsonb
            )
            """,
            (source_id,),
        )
    conn.rollback()


@pytest.mark.parametrize("value", [-0.001, 1.001])
def test_negative_reliability_prior_out_of_range(conn: Any, value: float) -> None:
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            """
            INSERT INTO public.source_registry (
                slug, name, source_class, reliability_tier, base_url, access_method,
                auth_requirement, allowed_paths, disallowed_paths, robots_status,
                max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
                language_codes, country_scope, topic_scope, update_frequency_hint,
                reliability_prior, strategic_relevance_score, enabled,
                created_at, updated_at, metadata
            ) VALUES (
                'synthetic_prior_bound', 'Synthetic Row', 'global_indicator', 'institutional',
                'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
                30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
                %s, 0.5, true, now(), now(), '{}'::jsonb
            )
            """,
            (value,),
        )
    conn.rollback()


def test_source_id_update_raises_trigger(conn: Any) -> None:
    row = conn.execute(
        INSERT_SQL + " RETURNING source_id",
        ("synthetic_immutable_id",),
    ).fetchone()
    assert row is not None
    with pytest.raises(psycopg.errors.RaiseException):
        conn.execute(
            "UPDATE public.source_registry SET source_id = uuid_generate_v4() WHERE slug = %s",
            ("synthetic_immutable_id",),
        )
    conn.rollback()


def test_zero_rows_after_negative_tests(conn: Any) -> None:
    count = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
    assert count is not None and count[0] == 0


NUMERIC_REQUESTS_EXPECTED: dict[str, Any] = {
    "name": "ck_source_registry_max_requests_per_minute",
    "contype": "c",
    "columns": ["max_requests_per_minute"],
    "numeric": {"column": "max_requests_per_minute", "ge": 0},
}

SOURCE_CLASS_VALUES = [
    "government_open_data",
    "legal_corpus",
    "global_indicator",
    "trade_data",
    "financial_disclosure",
    "investment_signal",
    "news_event",
    "benchmark_country",
    "report_library",
]
SOURCE_CLASS_EXPECTED: dict[str, Any] = {
    "name": "ck_source_registry_source_class",
    "contype": "c",
    "columns": ["source_class"],
    "values": SOURCE_CLASS_VALUES,
}
SOURCE_CLASS_LITERALS_SQL = ", ".join(f"'{value}'" for value in SOURCE_CLASS_VALUES)


def test_a4_rejects_extra_predicate_definition() -> None:
    definition = "CHECK ((max_requests_per_minute >= 0 AND max_requests_per_minute <> 29))"
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            NUMERIC_REQUESTS_EXPECTED,
            "c",
            definition,
            ["max_requests_per_minute"],
        )


def test_a4_rejects_wrong_column_definition() -> None:
    definition = "CHECK ((max_pages_per_cycle >= 0))"
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            NUMERIC_REQUESTS_EXPECTED,
            "c",
            definition,
            ["max_pages_per_cycle"],
        )


def test_a4_rejects_extra_predicate_and_wrong_column_in_disposable_schema(conn: Any) -> None:
    conn.execute("CREATE SCHEMA fath_a4_probe")
    conn.execute(
        """
        CREATE TABLE fath_a4_probe.probe (
            max_requests_per_minute integer NOT NULL,
            max_pages_per_cycle integer NOT NULL
        )
        """
    )
    conn.execute(
        """
        ALTER TABLE fath_a4_probe.probe
        ADD CONSTRAINT ck_source_registry_max_requests_per_minute
        CHECK (max_requests_per_minute >= 0 AND max_requests_per_minute <> 29)
        """
    )
    extra = conn.execute(
        """
        SELECT contype, pg_get_constraintdef(oid), conkey
        FROM pg_constraint
        WHERE conrelid = 'fath_a4_probe.probe'::regclass
          AND conname = 'ck_source_registry_max_requests_per_minute'
        """
    ).fetchone()
    assert extra is not None
    attnames = {
        row[0]: row[1]
        for row in conn.execute(
            """
            SELECT attnum, attname FROM pg_attribute
            WHERE attrelid = 'fath_a4_probe.probe'::regclass AND attnum > 0
            """
        )
    }
    extra_cols = [attnames[int(n)] for n in extra[2]]
    with pytest.raises(AssertionError):
        assert_constraint_semantics(NUMERIC_REQUESTS_EXPECTED, extra[0], extra[1], extra_cols)

    conn.execute(
        "ALTER TABLE fath_a4_probe.probe DROP CONSTRAINT ck_source_registry_max_requests_per_minute"
    )
    conn.execute(
        """
        ALTER TABLE fath_a4_probe.probe
        ADD CONSTRAINT ck_source_registry_max_requests_per_minute
        CHECK (max_pages_per_cycle >= 0)
        """
    )
    wrong = conn.execute(
        """
        SELECT contype, pg_get_constraintdef(oid), conkey
        FROM pg_constraint
        WHERE conrelid = 'fath_a4_probe.probe'::regclass
          AND conname = 'ck_source_registry_max_requests_per_minute'
        """
    ).fetchone()
    assert wrong is not None
    wrong_cols = [attnames[int(n)] for n in wrong[2]]
    with pytest.raises(AssertionError):
        assert_constraint_semantics(NUMERIC_REQUESTS_EXPECTED, wrong[0], wrong[1], wrong_cols)


def test_a4_rejects_self_referential_enum_definition() -> None:
    definition = (
        "CHECK ((source_class = ANY (ARRAY[" + SOURCE_CLASS_LITERALS_SQL + ", source_class])))"
    )
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            SOURCE_CLASS_EXPECTED,
            "c",
            definition,
            ["source_class"],
        )


@pytest.mark.parametrize(
    "array_sql",
    [
        ", ".join(f"lower('{value}')" for value in SOURCE_CLASS_VALUES),
        SOURCE_CLASS_LITERALS_SQL + ", NULL",
    ],
    ids=["lower_function", "null_element"],
)
def test_a4_rejects_nonconstant_enum_array_definition(array_sql: str) -> None:
    definition = f"CHECK ((source_class = ANY (ARRAY[{array_sql}])))"
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            SOURCE_CLASS_EXPECTED,
            "c",
            definition,
            ["source_class"],
        )


def test_a4_rejects_self_referential_and_nonconstant_enum_in_disposable_schema(conn: Any) -> None:
    conn.execute("CREATE SCHEMA fath_a4_enum_probe")
    conn.execute("CREATE TABLE fath_a4_enum_probe.probe (source_class text NOT NULL)")

    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe "
        "ADD CONSTRAINT ck_source_registry_source_class "
        f"CHECK (source_class = ANY (ARRAY[{SOURCE_CLASS_LITERALS_SQL}, source_class]))"
    )
    self_ref = conn.execute(
        """
        SELECT contype, pg_get_constraintdef(oid), conkey
        FROM pg_constraint
        WHERE conrelid = 'fath_a4_enum_probe.probe'::regclass
          AND conname = 'ck_source_registry_source_class'
        """
    ).fetchone()
    assert self_ref is not None
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            SOURCE_CLASS_EXPECTED, self_ref[0], self_ref[1], ["source_class"]
        )
    conn.execute("INSERT INTO fath_a4_enum_probe.probe VALUES ('not_a_real_class')")
    bogus_count = conn.execute("SELECT COUNT(*) FROM fath_a4_enum_probe.probe").fetchone()
    assert bogus_count is not None and bogus_count[0] == 1

    conn.execute("DELETE FROM fath_a4_enum_probe.probe")
    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe DROP CONSTRAINT ck_source_registry_source_class"
    )
    fn_elems = ", ".join(f"lower('{value}')" for value in SOURCE_CLASS_VALUES)
    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe "
        "ADD CONSTRAINT ck_source_registry_source_class "
        f"CHECK (source_class = ANY (ARRAY[{fn_elems}]))"
    )
    fn_row = conn.execute(
        """
        SELECT contype, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'fath_a4_enum_probe.probe'::regclass
          AND conname = 'ck_source_registry_source_class'
        """
    ).fetchone()
    assert fn_row is not None
    with pytest.raises(AssertionError):
        assert_constraint_semantics(SOURCE_CLASS_EXPECTED, fn_row[0], fn_row[1], ["source_class"])

    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe DROP CONSTRAINT ck_source_registry_source_class"
    )
    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe "
        "ADD CONSTRAINT ck_source_registry_source_class "
        f"CHECK (source_class = ANY (ARRAY[{SOURCE_CLASS_LITERALS_SQL}, NULL]))"
    )
    null_row = conn.execute(
        """
        SELECT contype, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'fath_a4_enum_probe.probe'::regclass
          AND conname = 'ck_source_registry_source_class'
        """
    ).fetchone()
    assert null_row is not None
    with pytest.raises(AssertionError):
        assert_constraint_semantics(
            SOURCE_CLASS_EXPECTED, null_row[0], null_row[1], ["source_class"]
        )

    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe DROP CONSTRAINT ck_source_registry_source_class"
    )
    conn.execute(
        "ALTER TABLE fath_a4_enum_probe.probe "
        "ADD CONSTRAINT ck_source_registry_source_class "
        f"CHECK (source_class IN ({SOURCE_CLASS_LITERALS_SQL}))"
    )
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO fath_a4_enum_probe.probe VALUES ('not_a_real_class')")
    conn.rollback()
