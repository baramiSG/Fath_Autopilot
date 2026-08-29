"""Migration 0002 — audit_log schema (DDL only, zero DML).

Transcribes docs/15 table, four named indexes, actor/action CHECKs, and a
BEFORE UPDATE OR DELETE append-only trigger. Full downgrade drops the
trigger, function, and table. Does not touch extensions.
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE public.audit_log (
            audit_id uuid NOT NULL,
            sequence_no BIGSERIAL NOT NULL,
            occurred_at timestamptz NOT NULL,
            actor_type text NOT NULL,
            actor_id text NOT NULL,
            action_type text NOT NULL,
            target_object_type text NOT NULL,
            target_object_id uuid,
            run_id uuid,
            event_id uuid,
            payload_hash_sha256 text NOT NULL,
            payload_canonical_json jsonb NOT NULL,
            previous_row_hash_sha256 text NOT NULL,
            row_hash_sha256 text NOT NULL,
            CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id),
            CONSTRAINT audit_log_sequence_no_key UNIQUE (sequence_no),
            CONSTRAINT audit_log_row_hash_sha256_key UNIQUE (row_hash_sha256),
            CONSTRAINT ck_audit_log_actor_type CHECK (actor_type IN (
                'agent',
                'user',
                'system'
            )),
            CONSTRAINT ck_audit_log_action_type CHECK (action_type IN (
                'source_accessed',
                'raw_archived',
                'content_sanitized',
                'fact_extracted',
                'fact_validated',
                'graph_updated',
                'hypothesis_created',
                'insight_promoted',
                'belief_created',
                'belief_calibrated',
                'approval_requested',
                'approval_decided',
                'budget_breached',
                'source_quarantined',
                'config_changed'
            ))
        )
        """
    )
    op.execute("CREATE INDEX idx_audit_time ON public.audit_log USING btree (occurred_at DESC)")
    op.execute(
        "CREATE INDEX idx_audit_target ON public.audit_log "
        "USING btree (target_object_type, target_object_id)"
    )
    op.execute("CREATE INDEX idx_audit_run ON public.audit_log USING btree (run_id)")
    op.execute("CREATE INDEX idx_audit_action ON public.audit_log USING btree (action_type)")
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


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS fath_audit_log_append_only()")
    op.execute("DROP TABLE IF EXISTS public.audit_log")
