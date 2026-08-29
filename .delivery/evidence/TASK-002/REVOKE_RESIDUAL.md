# TASK-002 residual: app-role REVOKE (IO-2)

FA-REQ-W1-007's requirement body includes "app role revoked update/delete".
This candidate does **not** implement GRANT/REVOKE.

Reasons this increment cannot implement it:

- Compose and CI connect as bootstrap role `fath` (`POSTGRES_USER`; `DATABASE_URL` user `fath`).
- `fath` is a PostgreSQL superuser in this slice. `REVOKE UPDATE, DELETE ON audit_log FROM fath` is a no-op against a superuser.
- No project authority defines a non-superuser application role or role credentials.
- Living DML detector `DDL_STATEMENT_HEADS` is `{CREATE, DROP, ALTER, COMMENT}`; a `GRANT`/`REVOKE` statement head fails IAC-001.

Acceptance for TASK-002 is met by BEFORE UPDATE OR DELETE row triggers that raise (`fath_audit_log_append_only` / `trg_audit_log_append_only`). Evidence must not claim revoke is implemented.

Forward owner (Flight Controller, not this candidate): register a roadmap open item routing dual-role / REVOKE to the W5–W6 ops decomposition or a Salim role-architecture decision (FATH-V4-001: an invariant with no owning task is a defect). This file must not be treated as modifying `.delivery/plans/**`.
