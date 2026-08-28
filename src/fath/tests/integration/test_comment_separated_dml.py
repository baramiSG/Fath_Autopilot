"""Prove comment-separated DML executes on PostgreSQL and is detected."""

from __future__ import annotations

from typing import Any

import psycopg
import pytest

from fath.tests.conftest import sync_database_url
from fath.tests.unit.test_migration_dml_discipline import check_source

pytestmark = pytest.mark.integration

COMMENT_SEPARATED_MIGRATION = '''
from alembic import op

def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_comment_dml (id int);
        INSERT/**/INTO public.source_registry (
            slug, name, source_class, reliability_tier, base_url, access_method,
            auth_requirement, allowed_paths, disallowed_paths, robots_status,
            max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
            language_codes, country_scope, topic_scope, update_frequency_hint,
            reliability_prior, strategic_relevance_score, enabled,
            created_at, updated_at, metadata
        ) VALUES (
            'synthetic_comment_dml', 'Synthetic Row', 'global_indicator', 'institutional',
            'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
            30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
            0.7, 0.5, true, now(), now(), '{}'::jsonb
        );
        DELETE/**/FROM public.source_registry WHERE slug = 'synthetic_comment_dml';
    """)
'''


def test_comment_separated_insert_delete_executes_and_is_detected() -> None:
    assert check_source(COMMENT_SEPARATED_MIGRATION, is_version_script=True)

    conn: psycopg.Connection[Any] = psycopg.connect(sync_database_url())
    try:
        before = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert before is not None and before[0] == 0
        inserted = conn.execute(
            """
            INSERT/**/INTO public.source_registry (
                slug, name, source_class, reliability_tier, base_url, access_method,
                auth_requirement, allowed_paths, disallowed_paths, robots_status,
                max_requests_per_minute, max_pages_per_cycle, max_bytes_per_cycle,
                language_codes, country_scope, topic_scope, update_frequency_hint,
                reliability_prior, strategic_relevance_score, enabled,
                created_at, updated_at, metadata
            ) VALUES (
                'synthetic_comment_dml', 'Synthetic Row', 'global_indicator', 'institutional',
                'https://example.com/row', 'api', 'none', '{}', '{}', 'unknown',
                30, 200, 500000000, '{en}', '{}', '{}', 'unknown',
                0.7, 0.5, true, now(), now(), '{}'::jsonb
            )
            """
        )
        assert inserted.statusmessage == "INSERT 0 1"
        mid = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert mid is not None and mid[0] == 1
        deleted = conn.execute(
            "DELETE/**/FROM public.source_registry WHERE slug = 'synthetic_comment_dml'"
        )
        assert deleted.statusmessage == "DELETE 1"
        after = conn.execute("SELECT COUNT(*) FROM public.source_registry").fetchone()
        assert after is not None and after[0] == 0
    finally:
        conn.rollback()
        conn.close()
