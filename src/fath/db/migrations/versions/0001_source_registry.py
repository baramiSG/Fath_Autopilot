"""Migration 0001 — source_registry schema (DDL only, zero DML).

Transcribes TASK-001_PLAN.md §6.0. Full downgrade implemented.
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS age")
    op.execute(
        """
        CREATE TABLE public.source_registry (
            source_id uuid NOT NULL DEFAULT uuid_generate_v4(),
            slug text NOT NULL,
            name text NOT NULL,
            source_class text NOT NULL,
            reliability_tier text NOT NULL,
            base_url text NOT NULL,
            api_base_url text,
            robots_url text,
            terms_url text,
            access_method text NOT NULL,
            auth_requirement text NOT NULL,
            subscription_name text,
            allowed_paths text[] NOT NULL,
            disallowed_paths text[] NOT NULL,
            robots_status text NOT NULL,
            max_requests_per_minute integer NOT NULL,
            max_pages_per_cycle integer NOT NULL,
            max_bytes_per_cycle bigint NOT NULL,
            language_codes text[] NOT NULL,
            country_scope text[] NOT NULL,
            topic_scope text[] NOT NULL,
            update_frequency_hint text NOT NULL,
            independence_group text,
            reliability_prior double precision NOT NULL,
            strategic_relevance_score double precision NOT NULL,
            data_quality_notes text,
            legal_notes text,
            enabled boolean NOT NULL,
            last_access_review_at timestamptz,
            created_at timestamptz NOT NULL,
            updated_at timestamptz NOT NULL,
            metadata jsonb NOT NULL,
            status text NOT NULL DEFAULT 'candidate'::text,
            CONSTRAINT source_registry_pkey PRIMARY KEY (source_id),
            CONSTRAINT source_registry_slug_key UNIQUE (slug),
            CONSTRAINT ck_source_registry_status CHECK (status IN (
                'candidate',
                'candidate_manual_review',
                'approved_inactive',
                'active',
                'suspended',
                'quarantined',
                'retired'
            )),
            CONSTRAINT ck_source_registry_source_class CHECK (source_class IN (
                'government_open_data',
                'legal_corpus',
                'global_indicator',
                'trade_data',
                'financial_disclosure',
                'investment_signal',
                'news_event',
                'benchmark_country',
                'report_library'
            )),
            CONSTRAINT ck_source_registry_reliability_tier CHECK (reliability_tier IN (
                'primary',
                'official_secondary',
                'institutional',
                'media',
                'low_confidence'
            )),
            CONSTRAINT ck_source_registry_access_method CHECK (access_method IN (
                'api',
                'bulk_download',
                'rss',
                'sitemap',
                'polite_crawl',
                'manual_ingestion',
                'disabled'
            )),
            CONSTRAINT ck_source_registry_auth_requirement CHECK (auth_requirement IN (
                'none',
                'api_key',
                'paid_subscription',
                'login_required',
                'not_allowed'
            )),
            CONSTRAINT ck_source_registry_robots_status CHECK (robots_status IN (
                'allowed',
                'disallowed',
                'partial',
                'not_applicable',
                'unknown'
            )),
            CONSTRAINT ck_source_registry_max_requests_per_minute
                CHECK (max_requests_per_minute >= 0),
            CONSTRAINT ck_source_registry_max_pages_per_cycle
                CHECK (max_pages_per_cycle >= 0),
            CONSTRAINT ck_source_registry_max_bytes_per_cycle
                CHECK (max_bytes_per_cycle >= 0),
            CONSTRAINT ck_source_registry_reliability_prior CHECK (
                reliability_prior >= 0 AND reliability_prior <= 1
            ),
            CONSTRAINT ck_source_registry_strategic_relevance_score CHECK (
                strategic_relevance_score >= 0 AND strategic_relevance_score <= 1
            )
        )
        """
    )
    op.execute("CREATE INDEX idx_sources_enabled ON public.source_registry USING btree (enabled)")
    op.execute(
        "CREATE INDEX idx_sources_class ON public.source_registry USING btree (source_class)"
    )
    op.execute(
        "CREATE INDEX idx_sources_reliability ON public.source_registry "
        "USING btree (reliability_tier)"
    )
    op.execute(
        "CREATE INDEX idx_sources_independence_group ON public.source_registry "
        "USING btree (independence_group)"
    )
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


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_source_registry_source_id_immutable ON source_registry")
    op.execute("DROP FUNCTION IF EXISTS fath_source_id_immutable()")
    op.execute("DROP TABLE IF EXISTS public.source_registry")
    op.execute("DROP EXTENSION IF EXISTS age")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
