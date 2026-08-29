"""Stdlib hash encoding and chain verification for audit_log (docs/15).

The docs/15 row-hash formula covers previous_row_hash_sha256, canonical JSON
payload, actor_id, action_type, target_object_id, and occurred_at_iso. It does
not cover actor_type, target_object_type, run_id, event_id, or
payload_hash_sha256. Those non-covered columns are protected only by the
append-only UPDATE/DELETE trigger.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence
from uuid import UUID

GENESIS_PREVIOUS_ROW_HASH = "0" * 64

_DUMPS_KWARGS: dict[str, object] = {
    "sort_keys": True,
    "separators": (",", ":"),
    "ensure_ascii": True,
    "allow_nan": False,
}


class PayloadEncodingError(ValueError):
    """Payload is not JSON-native or is not JSONB-round-trip stable."""


@dataclass(frozen=True)
class StoredAuditRow:
    """Verifier input built from stored column values only."""

    sequence_no: int
    actor_type: str
    actor_id: str
    action_type: str
    target_object_type: str
    target_object_id: UUID | None
    occurred_at: datetime
    payload: dict[str, Any]
    payload_hash_sha256: str
    previous_row_hash_sha256: str
    row_hash_sha256: str


@dataclass(frozen=True)
class ChainVerificationResult:
    ok: bool
    rows_checked: int
    failure_reason: str | None = None


def _reject_jsonb_unstable_numbers(obj: object, path: str = "$") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            _reject_jsonb_unstable_numbers(value, f"{path}.{key}")
        return
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            _reject_jsonb_unstable_numbers(value, f"{path}[{index}]")
        return
    if isinstance(obj, bool) or obj is None or isinstance(obj, str):
        return
    if isinstance(obj, int):
        return
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise PayloadEncodingError(f"NaN/Infinity at {path} is not JSONB-stable")
        if obj == 0.0 and math.copysign(1.0, obj) < 0.0:
            raise PayloadEncodingError(f"signed zero at {path} is not JSONB-stable")
        dumped = json.dumps(obj, ensure_ascii=True, allow_nan=False)
        if "e" in dumped.lower():
            raise PayloadEncodingError(f"exponent-form float at {path} is not JSONB-stable")
        return
    raise PayloadEncodingError(f"non-JSON-native value at {path}: {type(obj).__name__}")


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Canonical JSON UTF-8 bytes: sorted keys, compact separators, ASCII."""

    if not isinstance(payload, dict):
        raise PayloadEncodingError("payload must be a JSON object")
    _reject_jsonb_unstable_numbers(payload)
    try:
        text = json.dumps(payload, **_DUMPS_KWARGS)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise PayloadEncodingError("payload is not JSON-native") from exc
    parsed = json.loads(text)
    again = json.dumps(parsed, **_DUMPS_KWARGS)  # type: ignore[arg-type]
    encoded = text.encode("utf-8")
    if again.encode("utf-8") != encoded:
        raise PayloadEncodingError("codec round-trip changed canonical bytes")
    return encoded


def payload_hash_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def format_target_object_id(target_object_id: UUID | None) -> str:
    if target_object_id is None:
        return ""
    return str(target_object_id)


def format_occurred_at_iso(occurred_at: datetime) -> str:
    if occurred_at.tzinfo is None:
        raise ValueError("occurred_at must be timezone-aware UTC datetime")
    return occurred_at.astimezone(timezone.utc).isoformat()


def compute_row_hash_sha256(
    *,
    previous_row_hash_sha256: str,
    payload: Mapping[str, Any],
    actor_id: str,
    action_type: str,
    target_object_id: UUID | None,
    occurred_at: datetime,
) -> str:
    """Delimiter-less concat per docs/15, hashed as UTF-8 SHA-256 hex."""

    concat = (
        previous_row_hash_sha256
        + canonical_json_bytes(payload).decode("utf-8")
        + actor_id
        + action_type
        + format_target_object_id(target_object_id)
        + format_occurred_at_iso(occurred_at)
    )
    return hashlib.sha256(concat.encode("utf-8")).hexdigest()


def verify_chain(
    rows: Sequence[StoredAuditRow],
    *,
    initial_previous_hash: str | None = None,
) -> ChainVerificationResult:
    """Order by sequence_no; check hash adjacency, never numeric contiguity.

    Recomputes payload_hash_sha256 and row_hash_sha256 from stored column
    values and never trusts stored hashes as inputs to the formula.

    ``initial_previous_hash`` seeds the walk. ``None`` means the window
    includes the chain head and must start from ``GENESIS_PREVIOUS_ROW_HASH``.
    """

    ordered = sorted(rows, key=lambda row: row.sequence_no)
    previous_hash = (
        GENESIS_PREVIOUS_ROW_HASH if initial_previous_hash is None else initial_previous_hash
    )
    for index, row in enumerate(ordered):
        try:
            expected_payload_hash = payload_hash_sha256(row.payload)
        except PayloadEncodingError as exc:
            return ChainVerificationResult(
                ok=False,
                rows_checked=index,
                failure_reason=f"sequence_no={row.sequence_no} payload encoding: {exc}",
            )
        if expected_payload_hash != row.payload_hash_sha256:
            return ChainVerificationResult(
                ok=False,
                rows_checked=index,
                failure_reason=(
                    f"sequence_no={row.sequence_no} stored payload_hash_sha256 "
                    "does not match recomputation from stored payload"
                ),
            )
        expected_row_hash = compute_row_hash_sha256(
            previous_row_hash_sha256=row.previous_row_hash_sha256,
            payload=row.payload,
            actor_id=row.actor_id,
            action_type=row.action_type,
            target_object_id=row.target_object_id,
            occurred_at=row.occurred_at,
        )
        if expected_row_hash != row.row_hash_sha256:
            return ChainVerificationResult(
                ok=False,
                rows_checked=index,
                failure_reason=(
                    f"sequence_no={row.sequence_no} stored row_hash_sha256 "
                    "does not match recomputation from stored columns"
                ),
            )
        if row.previous_row_hash_sha256 != previous_hash:
            return ChainVerificationResult(
                ok=False,
                rows_checked=index,
                failure_reason=(
                    f"sequence_no={row.sequence_no} previous_row_hash_sha256 "
                    "is not adjacent to the prior row in sequence_no order"
                ),
            )
        previous_hash = row.row_hash_sha256
    return ChainVerificationResult(ok=True, rows_checked=len(ordered), failure_reason=None)


def verify_windowed_chain(
    rows: Sequence[StoredAuditRow],
    *,
    predecessor: StoredAuditRow | None = None,
    predecessor_is_chain_head: bool = False,
) -> ChainVerificationResult:
    """Verify a sequence-ordered window; genesis only where the head is in reach.

    When ``predecessor`` is omitted the window includes the table's first row
    and must chain from genesis. When it is supplied, that row is recomputed
    from stored columns and the walk is seeded from the recomputed
    ``row_hash_sha256`` (never from the stored hash as an unchecked continuum).

    ``predecessor_is_chain_head`` says the seed row is itself the table's first
    row in sequence order, so the genesis requirement still applies to it.
    Callers must leave it false whenever rows exist before the seed: those rows
    are outside the window and the seed cannot be anchored.
    """

    if predecessor is None:
        return verify_chain(rows)
    predecessor_check = verify_chain(
        [predecessor],
        initial_previous_hash=(
            GENESIS_PREVIOUS_ROW_HASH
            if predecessor_is_chain_head
            else predecessor.previous_row_hash_sha256
        ),
    )
    if not predecessor_check.ok:
        return ChainVerificationResult(
            ok=False,
            rows_checked=0,
            failure_reason=predecessor_check.failure_reason,
        )
    recomputed_predecessor_hash = compute_row_hash_sha256(
        previous_row_hash_sha256=predecessor.previous_row_hash_sha256,
        payload=predecessor.payload,
        actor_id=predecessor.actor_id,
        action_type=predecessor.action_type,
        target_object_id=predecessor.target_object_id,
        occurred_at=predecessor.occurred_at,
    )
    return verify_chain(rows, initial_previous_hash=recomputed_predecessor_hash)
