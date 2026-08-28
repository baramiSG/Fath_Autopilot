"""Prove the schema-qualified COPY ... FROM PROGRAM and UPDATE ONLY ... SET forms
execute live on PostgreSQL, can be concealed by savepoint rollback, and are now
rejected by the migration DML detector (FATH-IMPL-008 / IAC-001 residual-limit rule)."""

from __future__ import annotations

from typing import Any

import psycopg
import pytest

from fath.tests.conftest import sync_database_url
from fath.tests.unit.test_migration_dml_discipline import check_source

pytestmark = pytest.mark.integration

QUALIFIED_COPY_MIGRATION = '''
from alembic import op

def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_copy_probe (id int);
        SAVEPOINT synthetic_sp;
        COPY public.source_registry (slug, name) FROM PROGRAM 'echo synthetic';
        ROLLBACK TO SAVEPOINT synthetic_sp;
    """)
'''

UPDATE_ONLY_MIGRATION = '''
from alembic import op

def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_update_probe (id int);
        UPDATE ONLY public.source_registry SET name = 'synthetic' WHERE slug = 'synthetic_x';
    """)
'''

# COPY the full set of NOT-NULL columns (source_id and status take their DB defaults),
# tab-delimited, produced by a server-side program — the reviewer-demonstrated form.
_COPY_PROGRAM = (
    "printf 'synthetic_probe_row\\tSynthetic Probe\\tglobal_indicator\\tinstitutional\\t"
    "https://example.com/probe\\tapi\\tnone\\t{}\\t{}\\tunknown\\t30\\t200\\t500000000\\t"
    "{en}\\t{}\\t{}\\tunknown\\t0.7\\t0.5\\tt\\t2026-01-01 00:00:00+00\\t"
    "2026-01-01 00:00:00+00\\t{}\\n'"
)
_COPY_STATEMENT = (
    "COPY public.source_registry (slug, name, source_class, reliability_tier, base_url, "
    "access_method, auth_requirement, allowed_paths, disallowed_paths, robots_status, "
    "max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle, language_codes, "
    "country_scope, topic_scope, update_frequency_hint, reliability_prior, "
    "strategic_relevance_score, enabled, created_at, updated_at, metadata) "
    f"FROM PROGRAM $cmd${_COPY_PROGRAM}$cmd$"
)


def _migration_wrapping(sql: str) -> str:
    return (
        "from alembic import op\n\n"
        "def upgrade() -> None:\n"
        '    op.execute("""\n'
        "        CREATE TABLE IF NOT EXISTS synthetic_copy_probe (id int);\n"
        f"        {sql};\n"
        '    """)\n'
    )


def test_qualified_copy_from_program_executes_is_concealed_and_is_detected() -> None:
    assert check_source(QUALIFIED_COPY_MIGRATION, is_version_script=True)
    assert check_source(_migration_wrapping(_COPY_STATEMENT), is_version_script=True)

    conn: psycopg.Connection[Any] = psycopg.connect(sync_database_url())
    try:
        before = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert before is not None and before[0] == 0

        conn.execute("SAVEPOINT synthetic_sp")
        copied = conn.execute(_COPY_STATEMENT)
        assert copied.statusmessage == "COPY 1"
        during = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert during is not None and during[0] == 1

        # Savepoint rollback conceals the write from all A12 zero-row observations.
        conn.execute("ROLLBACK TO SAVEPOINT synthetic_sp")
        after = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert after is not None and after[0] == 0
    finally:
        conn.rollback()
        conn.close()


def test_update_only_set_executes_live_and_is_detected() -> None:
    assert check_source(UPDATE_ONLY_MIGRATION, is_version_script=True)

    conn: psycopg.Connection[Any] = psycopg.connect(sync_database_url())
    try:
        before = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert before is not None and before[0] == 0
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
                'synthetic_probe_row', 'Synthetic Probe', 'global_indicator', 'institutional',
                'https://example.com/probe', 'api', 'none', '{}', '{}', 'unknown',
                30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
                0.7, 0.5, true, now(), now(), '{}'::jsonb
            )
            """
        )
        updated = conn.execute(
            "UPDATE ONLY public.source_registry SET name = 'Synthetic Probe 2' "
            "WHERE slug = 'synthetic_probe_row'"
        )
        assert updated.statusmessage == "UPDATE 1"
        live_update = (
            "from alembic import op\n\n"
            "def upgrade() -> None:\n"
            '    op.execute("""\n'
            "        CREATE TABLE IF NOT EXISTS synthetic_update_probe (id int);\n"
            "        UPDATE ONLY public.source_registry SET name = 'Synthetic Probe 2' "
            "WHERE slug = 'synthetic_probe_row';\n"
            '    """)\n'
        )
        assert check_source(live_update, is_version_script=True)
    finally:
        conn.rollback()
        after = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert after is not None and after[0] == 0
        conn.close()
