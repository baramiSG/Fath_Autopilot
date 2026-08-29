# TASK-002 ADR-style layout note (IO-14 / docs/23 anti-drift)

docs/16 enumerates `db/models/audit_log.py` but does not list `db/audit_hash.py` or `db/audit_repo.py`. Those two files are still under the canonical `db` module (not a new top-level package).

Justification:

- docs/24 §8 names the write surface `audit_repo.append_in_transaction` and forbids async SQLAlchemy event listeners.
- A13c contains SQLAlchemy to one exact new path: `src/fath/db/audit_repo.py` (plus existing `connection.py`, `migrations/`, and `tests/`).
- `db/models/audit_log.py` remains pydantic/stdlib-only, matching `source_registry.py`.
- `db/audit_hash.py` is stdlib-only (hashlib/json) so writer and verifier share one encoding module.
- `memory/` remains reserved for the five stores; no SQLAlchemy writers there.
- FATH-PR-002 / REMEDIATION-1 rejected a `src/fath/audit/` package. A5 `doc16_modules` still rejects that path.

This note lives under `.delivery/evidence/TASK-002/` because the candidate must not modify `.delivery/plans/**`.
