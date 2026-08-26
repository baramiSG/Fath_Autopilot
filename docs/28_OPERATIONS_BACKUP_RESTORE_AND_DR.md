# 28 — Operations, Backup, Restore, and Disaster Recovery

## Purpose

Fath is designed to run continuously. This document specifies operational controls: backups, restore tests, migrations, monitoring, incident response, and disaster recovery.

## Production services

```text
FastAPI backend
Next.js frontend
Postgres 16 + Apache AGE + pgvector
Redis 7
MinIO or Azure Blob
Prefect server/worker
vLLM embedding server
vLLM reranker server
OCR/layout workers
Simulation sandbox worker
Caddy reverse proxy
```

## Backup scope

| Asset | Backup required | Frequency |
|---|---:|---:|
| Postgres database | Yes | Continuous WAL + daily full |
| MinIO / Blob raw artifacts | Yes | Daily incremental |
| Source YAML definitions | Yes | Git repository |
| `.env` secrets | No plain backup | Azure Key Vault only |
| Audit log | Yes | Included in Postgres + weekly verification |
| Redis Streams | Best effort | Operational, not source of truth |
| Prefect metadata | Yes | Daily DB backup if self-hosted |
| Frontend/backend code | Yes | Git repository |

## Postgres backup

### Daily full backup

```bash
pg_dump --format=custom --file=/backups/postgres/fath_$(date +%Y%m%d).dump $DATABASE_URL
```

### Continuous WAL archiving

Use `archive_mode=on` and store WAL segments in object storage.

```conf
archive_mode = on
archive_command = 'cp %p /backups/wal/%f'
wal_level = replica
```

Production may use Azure-native backup if the database is managed. If self-hosted on the VM, use WAL archiving.

## Object storage backup

Raw artifacts are critical because every fact must trace back to raw evidence.

```text
MinIO bucket: fath-raw-archive
Backup: daily mirror to secondary bucket/path
Verification: compare object count and sample content_hashes
```

Command pattern:

```bash
mc mirror --overwrite minio/fath-raw-archive minio-backup/fath-raw-archive
```

## Restore drill

Run monthly.

```text
1. Create clean restore environment.
2. Restore Postgres from backup.
3. Restore raw archive objects.
4. Run migrations to current head if needed.
5. Run audit chain verification.
6. Sample 100 facts and verify raw_archive_refs resolve to objects.
7. Run golden eval smoke test.
8. Produce restore report.
```

## Restore report schema

```python
class RestoreReport(BaseModel):
    report_id: UUID
    started_at: datetime
    completed_at: datetime
    postgres_restored: bool
    object_store_restored: bool
    audit_chain_verified: bool
    sampled_facts_checked: int
    sampled_facts_missing_raw: int
    golden_eval_passed: bool
    notes: str = ""
```

```sql
CREATE TABLE restore_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    postgres_restored BOOLEAN NOT NULL,
    object_store_restored BOOLEAN NOT NULL,
    audit_chain_verified BOOLEAN NOT NULL,
    sampled_facts_checked INTEGER NOT NULL,
    sampled_facts_missing_raw INTEGER NOT NULL,
    golden_eval_passed BOOLEAN NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
```

## RPO / RTO targets

| Metric | Target |
|---|---:|
| RPO for Postgres | 1 hour |
| RPO for raw artifacts | 24 hours |
| RTO for dev/demo environment | 4 hours |
| RTO for production environment | 24 hours |

## Migration policy

Migrations are applied through Alembic.

Rules:

```text
No destructive migrations without backup.
Every migration has upgrade and downgrade unless technically impossible.
Schema changes to Pydantic models require migration in same step.
Migrations run in staging before production.
Audit log schema changes require explicit verifier approval.
```

Migration test:

```bash
alembic upgrade head
pytest tests/db/test_migrations.py
alembic downgrade -1
alembic upgrade head
```

## Observability

### Metrics

Prometheus metrics:

```text
fath_heartbeat_runs_total{cadence,status}
fath_heartbeat_duration_seconds{cadence}
fath_raw_archive_records_total{source_id}
fath_facts_extracted_total{claim_type}
fath_graph_edges_total{edge_type}
fath_llm_calls_total{agent_role}
fath_budget_consumed_pct{scope,resource}
fath_poisoning_signals_total{severity,kind}
fath_audit_chain_verification_status
fath_canvas_stream_clients
```

### Logs

All services use JSON structured logs with:

```text
run_id
trace_id
agent_role
source_id
event_type
correlation_id
```

### Traces

OpenTelemetry traces span:

```text
workflow run
agent run
LLM call
crawler request
DB write
event emit
Canvas render spec generation
```

## Health checks

```text
GET /healthz    shallow: process alive
GET /readyz     deep: DB, Redis, object store, event bus, source registry loaded
GET /metrics    Prometheus
```

Readiness fails if:

```text
Postgres unavailable
Redis unavailable
source registry cannot load
latest audit verification failed critically
object store unavailable
```

## Incident response

### Critical incidents

```text
source-poisoning critical signal
audit chain break
unauthorized approval attempt
budget runaway
crawler violates Access Guard
raw archive object missing
Sanad publishes without evidence bundle
```

### Response sequence

```text
1. Stop affected workflow or source.
2. Preserve logs and audit rows.
3. Quarantine affected facts/sources if data integrity risk.
4. Run audit verifier.
5. Run restore check if corruption suspected.
6. Record incident report.
7. Resume only after operator approval.
```

## Incident report schema

```sql
CREATE TABLE incident_reports (
    incident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    severity TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    detected_by TEXT NOT NULL,
    affected_components TEXT[] NOT NULL DEFAULT '{}',
    containment_actions JSONB NOT NULL DEFAULT '[]'::jsonb,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);
```

## Secrets management

Production secrets live in Azure Key Vault. `.env` files are for local development only.

Secrets:

```text
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
DATABASE_URL
REDIS_URL
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
COMTRADE_API_KEY, if used
OIDC_CLIENT_SECRET
JWT_SIGNING_KEY, local only
```

No secret is written to:

```text
audit log
structured logs
event payloads
Canvas specs
raw archive
```

## Runbooks

### Restart hourly workflows

```bash
prefect deployment run fath-hourly/fath-hourly
```

### Verify audit chain

```bash
python scripts/verify_audit_chain.py --recent 10000
```

### Quarantine a source manually

```bash
python scripts/quarantine_source.py --source-id SOURCE --reason "operator review"
```

### Restore from backup

```bash
scripts/restore_from_backup.sh --date YYYYMMDD --target restore_env
```

## Production readiness gate

Before continuous operation:

1. Backup succeeds.
2. Restore drill succeeds.
3. Audit verification succeeds.
4. Health/readiness endpoints pass.
5. Metrics visible.
6. Alert routing configured.
7. Source registry active set verified.
8. RBAC enforced.
9. Secrets loaded from Key Vault.
10. No crawler runs with `manual_review` source active.
