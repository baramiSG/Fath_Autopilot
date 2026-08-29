"""Pattern A in-transaction audit_log writer (docs/24 §8; docs/15 columns)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Literal, Mapping
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from fath.db.audit_hash import (
    GENESIS_PREVIOUS_ROW_HASH,
    ChainVerificationResult,
    PayloadEncodingError,
    StoredAuditRow,
    canonical_json_bytes,
    compute_row_hash_sha256,
    format_occurred_at_iso,
    payload_hash_sha256,
    verify_windowed_chain,
)
from fath.db.models.audit_log import AuditActionType, AuditLogRecord

_FETCH_COLUMNS = """
    sequence_no, actor_type, actor_id, action_type,
    target_object_type, target_object_id, occurred_at,
    CAST(payload_canonical_json AS text) AS payload_canonical_json,
    payload_hash_sha256, previous_row_hash_sha256, row_hash_sha256
"""


def _coerce_action_type(action_type: AuditActionType | str) -> str:
    if isinstance(action_type, AuditActionType):
        return action_type.value
    return AuditActionType(action_type).value


def _row_from_mapping(mapping: Mapping[Any, Any]) -> StoredAuditRow:
    raw_payload = mapping["payload_canonical_json"]
    if isinstance(raw_payload, str):
        decoded: object = json.loads(raw_payload)
    else:
        decoded = raw_payload
    if not isinstance(decoded, dict):
        raise PayloadEncodingError("stored payload_canonical_json is not an object")
    return StoredAuditRow(
        sequence_no=int(mapping["sequence_no"]),
        actor_type=str(mapping["actor_type"]),
        actor_id=str(mapping["actor_id"]),
        action_type=str(mapping["action_type"]),
        target_object_type=str(mapping["target_object_type"]),
        target_object_id=mapping["target_object_id"],
        occurred_at=mapping["occurred_at"],
        payload=decoded,
        payload_hash_sha256=str(mapping["payload_hash_sha256"]),
        previous_row_hash_sha256=str(mapping["previous_row_hash_sha256"]),
        row_hash_sha256=str(mapping["row_hash_sha256"]),
    )


async def fetch_audit_rows(
    session: AsyncSession,
    *,
    recent: int | None = None,
) -> list[StoredAuditRow]:
    """Load stored audit rows ordered by sequence_no (gap-tolerant)."""

    if recent is None:
        result = await session.execute(
            text(f"SELECT {_FETCH_COLUMNS} FROM audit_log ORDER BY sequence_no")
        )
    else:
        result = await session.execute(
            text(
                f"SELECT {_FETCH_COLUMNS} FROM ("
                f" SELECT {_FETCH_COLUMNS} FROM audit_log"
                " ORDER BY sequence_no DESC LIMIT :recent"
                ") scoped ORDER BY sequence_no"
            ),
            {"recent": recent},
        )
    return [_row_from_mapping(row._mapping) for row in result]


async def _row_exists_before(session: AsyncSession, sequence_no: int) -> bool:
    """Whether any row precedes ``sequence_no`` (gap-tolerant existence test)."""

    result = await session.execute(
        text("SELECT 1 FROM audit_log WHERE sequence_no < :sequence_no LIMIT 1"),
        {"sequence_no": sequence_no},
    )
    return result.first() is not None


async def verify_recent_chain(session: AsyncSession, *, recent: int) -> ChainVerificationResult:
    """Windowed chain verification used by the CLI ``--recent`` path.

    Fetches ``recent + 1`` newest rows. If the table has at most ``recent`` rows
    the window itself includes the chain head and genesis is required. Otherwise
    the extra row is recomputed and used as the seed, and the database decides
    whether that seed is the table's first row: if it is, genesis still applies,
    because a window reaching the head must not accept a rewritten anchor.
    """

    if recent < 0:
        raise ValueError("recent must be a non-negative row count")
    fetched = await fetch_audit_rows(session, recent=recent + 1)
    if len(fetched) <= recent:
        return verify_windowed_chain(fetched, predecessor=None)
    seed = fetched[0]
    return verify_windowed_chain(
        fetched[1:],
        predecessor=seed,
        predecessor_is_chain_head=not await _row_exists_before(session, seed.sequence_no),
    )


async def append_in_transaction(
    session: AsyncSession,
    *,
    actor_type: Literal["agent", "user", "system"],
    actor_id: str,
    action_type: AuditActionType | str,
    target_object_type: str,
    target_object_id: UUID | None,
    payload: Mapping[str, Any],
    run_id: UUID | None = None,
    event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> AuditLogRecord:
    """Insert one hash-chained audit row on the caller's open transaction.

    Returns the persisted ``AuditLogRecord``. ``sequence_no`` is assigned by
    BIGSERIAL and is never writer-supplied. ``audit_id`` is generated here.
    """

    if not session.in_transaction():
        raise RuntimeError("append_in_transaction requires an open transaction")
    if actor_type not in {"agent", "user", "system"}:
        raise ValueError("actor_type must be agent, user, or system")
    if not isinstance(payload, dict):
        raise PayloadEncodingError("payload must be a JSON object")

    action_value = _coerce_action_type(action_type)
    occurred = occurred_at if occurred_at is not None else datetime.now(timezone.utc)
    if occurred.tzinfo is None:
        raise ValueError("occurred_at must be timezone-aware")
    occurred_utc = occurred.astimezone(timezone.utc)
    expected_iso = format_occurred_at_iso(occurred_utc)

    canonical = canonical_json_bytes(payload)
    probe = await session.execute(
        text("SELECT CAST(CAST(:canonical AS jsonb) AS text)"),
        {"canonical": canonical.decode("utf-8")},
    )
    loaded_text = probe.scalar_one()
    if not isinstance(loaded_text, str):
        raise PayloadEncodingError("JSONB text probe did not return text")
    loaded: object = json.loads(loaded_text)
    if not isinstance(loaded, dict):
        raise PayloadEncodingError("JSONB did not return an object")
    if canonical_json_bytes(loaded) != canonical:
        raise PayloadEncodingError("payload is not JSONB-stable")

    await session.execute(text("LOCK TABLE audit_log IN EXCLUSIVE MODE"))
    latest = await session.execute(
        text("SELECT row_hash_sha256 FROM audit_log ORDER BY sequence_no DESC LIMIT 1")
    )
    latest_row = latest.first()
    previous_hash = str(latest_row[0]) if latest_row is not None else GENESIS_PREVIOUS_ROW_HASH

    payload_hash = payload_hash_sha256(payload)
    row_hash = compute_row_hash_sha256(
        previous_row_hash_sha256=previous_hash,
        payload=payload,
        actor_id=actor_id,
        action_type=action_value,
        target_object_id=target_object_id,
        occurred_at=occurred_utc,
    )
    audit_id = uuid4()
    inserted = await session.execute(
        text(
            """
            INSERT INTO audit_log (
                audit_id, occurred_at, actor_type, actor_id, action_type,
                target_object_type, target_object_id, run_id, event_id,
                payload_hash_sha256, payload_canonical_json,
                previous_row_hash_sha256, row_hash_sha256
            ) VALUES (
                :audit_id, :occurred_at, :actor_type, :actor_id, :action_type,
                :target_object_type, :target_object_id, :run_id, :event_id,
                :payload_hash_sha256, CAST(:payload_canonical_json AS jsonb),
                :previous_row_hash_sha256, :row_hash_sha256
            )
            RETURNING sequence_no, occurred_at,
                      CAST(payload_canonical_json AS text) AS payload_canonical_json
            """
        ),
        {
            "audit_id": audit_id,
            "occurred_at": occurred_utc,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "action_type": action_value,
            "target_object_type": target_object_type,
            "target_object_id": target_object_id,
            "run_id": run_id,
            "event_id": event_id,
            "payload_hash_sha256": payload_hash,
            "payload_canonical_json": canonical.decode("utf-8"),
            "previous_row_hash_sha256": previous_hash,
            "row_hash_sha256": row_hash,
        },
    )
    returned = inserted.one()
    stored_occurred = returned.occurred_at
    if format_occurred_at_iso(stored_occurred) != expected_iso:
        raise PayloadEncodingError("occurred_at TIMESTAMPTZ round-trip changed isoformat bytes")
    stored_payload_raw = returned.payload_canonical_json
    if isinstance(stored_payload_raw, str):
        stored_payload_obj: object = json.loads(stored_payload_raw)
    else:
        stored_payload_obj = stored_payload_raw
    if not isinstance(stored_payload_obj, dict):
        raise PayloadEncodingError("stored payload_canonical_json is not an object")
    stored_payload = stored_payload_obj
    recomputed = compute_row_hash_sha256(
        previous_row_hash_sha256=previous_hash,
        payload=stored_payload,
        actor_id=actor_id,
        action_type=action_value,
        target_object_id=target_object_id,
        occurred_at=stored_occurred,
    )
    if recomputed != row_hash:
        raise PayloadEncodingError("stored columns do not recompute to the written row hash")

    return AuditLogRecord(
        audit_id=audit_id,
        sequence_no=int(returned.sequence_no),
        occurred_at=stored_occurred,
        actor_type=actor_type,
        actor_id=actor_id,
        action_type=AuditActionType(action_value),
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        run_id=run_id,
        event_id=event_id,
        payload_hash_sha256=payload_hash,
        payload_canonical_json=stored_payload,
        previous_row_hash_sha256=previous_hash,
        row_hash_sha256=row_hash,
    )
