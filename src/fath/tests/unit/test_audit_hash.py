"""Byte-exact docs/15 hash encoding and gap-tolerant chain verification."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from fath.db.audit_hash import (
    GENESIS_PREVIOUS_ROW_HASH,
    PayloadEncodingError,
    StoredAuditRow,
    canonical_json_bytes,
    compute_row_hash_sha256,
    format_occurred_at_iso,
    format_target_object_id,
    payload_hash_sha256,
    verify_chain,
    verify_windowed_chain,
)

SYNTHETIC_ACTOR = "synthetic_actor"
ACTION_CONFIG = "config_changed"
ZERO_US = datetime(2026, 1, 1, tzinfo=timezone.utc)
WITH_US = datetime(2026, 1, 1, 12, 34, 56, 123456, tzinfo=timezone.utc)
SYNTHETIC_UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PAYLOAD = {"n": 1, "synthetic": True}
CANONICAL = b'{"n":1,"synthetic":true}'
PAYLOAD_HASH = "5783d2ecfe819ff75a6a1b1bf2ce9eba2370ea9c8f58eda070286b341e926880"
GENESIS_ROW_HASH = "45e5eeb6dfbef0dc2f5ab92aa163ff7c7b9e81b3dd8e7d16a2b97f263656ccc8"
NON_GENESIS_ANCHOR = "f" * 64


def test_genesis_previous_hash_is_64_zero_hex() -> None:
    assert GENESIS_PREVIOUS_ROW_HASH == "0" * 64
    assert len(GENESIS_PREVIOUS_ROW_HASH) == 64


def test_canonical_json_bytes_sorted_compact_ascii() -> None:
    assert canonical_json_bytes(PAYLOAD) == CANONICAL
    nested = {"b": {"a": 1}, "a": [1, {"z": 2}]}
    assert canonical_json_bytes(nested) == b'{"a":[1,{"z":2}],"b":{"a":1}}'


def test_non_ascii_uses_ensure_ascii_escapes() -> None:
    assert canonical_json_bytes({"ar": "مرحبا"}) == b'{"ar":"\\u0645\\u0631\\u062d\\u0628\\u0627"}'


def test_codec_round_trip_rejects_mismatch() -> None:
    assert canonical_json_bytes({"n": 1e-3}) == b'{"n":0.001}'


def test_signed_zero_rejected() -> None:
    with pytest.raises(PayloadEncodingError, match="JSONB"):
        canonical_json_bytes({"n": -0.0})


def test_exponent_form_float_rejected() -> None:
    with pytest.raises(PayloadEncodingError, match="JSONB"):
        canonical_json_bytes({"n": 1e300})


def test_nan_and_infinity_rejected() -> None:
    with pytest.raises(PayloadEncodingError):
        canonical_json_bytes({"n": float("nan")})
    with pytest.raises(PayloadEncodingError):
        canonical_json_bytes({"n": float("inf")})


def test_int_greater_than_float53_stays_integer_text() -> None:
    value = 2**53 + 1
    assert canonical_json_bytes({"n": value}) == b'{"n":9007199254740993}'


def test_non_json_native_payload_rejected() -> None:
    with pytest.raises(PayloadEncodingError):
        canonical_json_bytes({"when": ZERO_US})
    with pytest.raises(PayloadEncodingError):
        canonical_json_bytes({"id": SYNTHETIC_UUID})


def test_none_uuid_is_empty_string() -> None:
    assert format_target_object_id(None) == ""


def test_uuid_is_lowercase_hyphenated() -> None:
    assert format_target_object_id(SYNTHETIC_UUID) == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def test_occurred_at_isoformat_zero_and_microseconds() -> None:
    assert format_occurred_at_iso(ZERO_US) == "2026-01-01T00:00:00+00:00"
    assert format_occurred_at_iso(WITH_US) == "2026-01-01T12:34:56.123456+00:00"


def test_naive_occurred_at_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        format_occurred_at_iso(datetime(2026, 1, 1))


def test_payload_hash_is_sha256_of_canonical_bytes() -> None:
    assert payload_hash_sha256(PAYLOAD) == PAYLOAD_HASH


def test_row_hash_genesis_vector() -> None:
    assert (
        compute_row_hash_sha256(
            previous_row_hash_sha256=GENESIS_PREVIOUS_ROW_HASH,
            payload=PAYLOAD,
            actor_id=SYNTHETIC_ACTOR,
            action_type=ACTION_CONFIG,
            target_object_id=None,
            occurred_at=ZERO_US,
        )
        == GENESIS_ROW_HASH
    )


def _row(
    *,
    sequence_no: int,
    previous: str,
    row_hash: str,
    actor_id: str = SYNTHETIC_ACTOR,
    action_type: str = ACTION_CONFIG,
    payload: dict[str, object] | None = None,
    occurred_at: datetime = ZERO_US,
    payload_hash: str = PAYLOAD_HASH,
    target_object_id: UUID | None = None,
    actor_type: str = "system",
    target_object_type: str = "synthetic_target",
) -> StoredAuditRow:
    return StoredAuditRow(
        sequence_no=sequence_no,
        actor_type=actor_type,
        actor_id=actor_id,
        action_type=action_type,
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        occurred_at=occurred_at,
        payload=dict(payload or PAYLOAD),
        payload_hash_sha256=payload_hash,
        previous_row_hash_sha256=previous,
        row_hash_sha256=row_hash,
    )


def test_verify_chain_empty_and_single_genesis() -> None:
    empty = verify_chain([])
    assert empty.ok is True
    assert empty.rows_checked == 0
    genesis = _row(sequence_no=1, previous=GENESIS_PREVIOUS_ROW_HASH, row_hash=GENESIS_ROW_HASH)
    result = verify_chain([genesis])
    assert result.ok is True
    assert result.rows_checked == 1


def test_verify_chain_is_gap_tolerant() -> None:
    second_hash = compute_row_hash_sha256(
        previous_row_hash_sha256=GENESIS_ROW_HASH,
        payload=PAYLOAD,
        actor_id=SYNTHETIC_ACTOR,
        action_type=ACTION_CONFIG,
        target_object_id=None,
        occurred_at=ZERO_US,
    )
    rows = [
        _row(sequence_no=1, previous=GENESIS_PREVIOUS_ROW_HASH, row_hash=GENESIS_ROW_HASH),
        _row(sequence_no=3, previous=GENESIS_ROW_HASH, row_hash=second_hash),
    ]
    result = verify_chain(rows)
    assert result.ok is True
    assert result.rows_checked == 2


def test_verify_recomputes_from_stored_values_not_stored_hashes() -> None:
    row = _row(
        sequence_no=1,
        previous=GENESIS_PREVIOUS_ROW_HASH,
        row_hash=GENESIS_ROW_HASH,
        payload_hash="0" * 64,
    )
    result = verify_chain([row])
    assert result.ok is False
    assert result.failure_reason is not None


def test_tamper_of_covered_actor_id_is_detected() -> None:
    """FA-REQ-W1-007 tamper oracle mutates a hash-covered field (actor_id)."""

    row = _row(sequence_no=1, previous=GENESIS_PREVIOUS_ROW_HASH, row_hash=GENESIS_ROW_HASH)
    tampered = _row(
        sequence_no=1,
        previous=GENESIS_PREVIOUS_ROW_HASH,
        row_hash=GENESIS_ROW_HASH,
        actor_id="mutated_actor",
    )
    assert verify_chain([row]).ok is True
    result = verify_chain([tampered])
    assert result.ok is False


def test_uncovered_actor_type_does_not_change_row_hash() -> None:
    """Non-covered columns (actor_type, target_object_type, run_id, event_id,
    payload_hash_sha256) are not in the docs/15 formula. Database triggers are
    the only protection against mutating them in place.
    """

    covered = compute_row_hash_sha256(
        previous_row_hash_sha256=GENESIS_PREVIOUS_ROW_HASH,
        payload=PAYLOAD,
        actor_id=SYNTHETIC_ACTOR,
        action_type=ACTION_CONFIG,
        target_object_id=None,
        occurred_at=ZERO_US,
    )
    row = _row(
        sequence_no=1,
        previous=GENESIS_PREVIOUS_ROW_HASH,
        row_hash=covered,
        actor_type="agent",
    )
    assert verify_chain([row]).ok is True


def _chain_from_anchor(anchor: str) -> list[StoredAuditRow]:
    """Internally consistent three-row chain seeded from ``anchor``.

    Every row recomputes from its own stored columns, so only the anchor
    distinguishes a genesis-rooted chain from a rewritten one.
    """

    second_actor = "synthetic_actor_b"
    third_payload: dict[str, object] = {"n": 2, "synthetic": True}
    specs = (
        (1, PAYLOAD, SYNTHETIC_ACTOR, PAYLOAD_HASH),
        (2, PAYLOAD, second_actor, PAYLOAD_HASH),
        (3, third_payload, SYNTHETIC_ACTOR, payload_hash_sha256(third_payload)),
    )
    rows: list[StoredAuditRow] = []
    previous = anchor
    for sequence_no, payload, actor_id, payload_hash in specs:
        row_hash = compute_row_hash_sha256(
            previous_row_hash_sha256=previous,
            payload=payload,
            actor_id=actor_id,
            action_type=ACTION_CONFIG,
            target_object_id=None,
            occurred_at=ZERO_US,
        )
        rows.append(
            _row(
                sequence_no=sequence_no,
                previous=previous,
                row_hash=row_hash,
                actor_id=actor_id,
                payload=dict(payload),
                payload_hash=payload_hash,
            )
        )
        previous = row_hash
    return rows


def _three_row_chain() -> list[StoredAuditRow]:
    """In-memory linear chain: genesis plus two successors."""

    rows = _chain_from_anchor(GENESIS_PREVIOUS_ROW_HASH)
    assert rows[0].row_hash_sha256 == GENESIS_ROW_HASH
    return rows


def _rewritten_chain() -> list[StoredAuditRow]:
    """Same rows re-linked from a non-genesis anchor (rewritten head)."""

    return _chain_from_anchor(NON_GENESIS_ANCHOR)


def test_verify_chain_mid_window_without_seed_still_requires_genesis() -> None:
    """Full-chain verify_chain keeps the genesis seed; windowed API is separate."""

    rows = _three_row_chain()
    result = verify_chain(rows[1:])
    assert result.ok is False
    assert result.failure_reason is not None
    assert "not adjacent" in result.failure_reason


def test_window_includes_genesis_still_enforces_genesis_seed() -> None:
    rows = _three_row_chain()
    head = verify_windowed_chain(rows[:1], predecessor=None)
    assert head.ok is True
    assert head.rows_checked == 1
    mid_as_head = verify_windowed_chain(rows[1:2], predecessor=None)
    assert mid_as_head.ok is False
    assert mid_as_head.failure_reason is not None
    assert "not adjacent" in mid_as_head.failure_reason


def test_mid_chain_window_with_correct_predecessor_seed_passes() -> None:
    rows = _three_row_chain()
    result = verify_windowed_chain(rows[1:], predecessor=rows[0])
    assert result.ok is True
    assert result.rows_checked == 2


def test_mid_chain_window_with_tampered_seed_row_fails() -> None:
    rows = _three_row_chain()
    tampered_seed = _row(
        sequence_no=rows[0].sequence_no,
        previous=rows[0].previous_row_hash_sha256,
        row_hash=rows[0].row_hash_sha256,
        actor_id="mutated_actor",
    )
    result = verify_windowed_chain(rows[1:], predecessor=tampered_seed)
    assert result.ok is False
    assert result.failure_reason is not None


def test_single_row_window_passes() -> None:
    rows = _three_row_chain()
    genesis_only = verify_windowed_chain(rows[:1], predecessor=None)
    assert genesis_only.ok is True
    assert genesis_only.rows_checked == 1
    tail = verify_windowed_chain(rows[2:], predecessor=rows[1])
    assert tail.ok is True
    assert tail.rows_checked == 1


def test_chain_head_predecessor_still_requires_genesis() -> None:
    """A seed row that is the table's first row keeps the genesis requirement.

    Without this the seed is accepted on internal consistency alone, so a chain
    rewritten from a forged anchor verifies clean.
    """

    rows = _rewritten_chain()
    result = verify_windowed_chain(rows[1:], predecessor=rows[0], predecessor_is_chain_head=True)
    assert result.ok is False
    assert result.failure_reason is not None
    assert "not adjacent" in result.failure_reason
    assert f"sequence_no={rows[0].sequence_no}" in result.failure_reason


def test_genuine_chain_head_predecessor_passes_genesis_check() -> None:
    """The same flag must not reject a real genesis-rooted head."""

    rows = _three_row_chain()
    result = verify_windowed_chain(rows[1:], predecessor=rows[0], predecessor_is_chain_head=True)
    assert result.ok is True
    assert result.rows_checked == 2


def test_mid_chain_predecessor_does_not_require_genesis() -> None:
    """Windows that never reach the head stay seedable from the predecessor.

    This is the bounded-window limit of ``--recent``, not a defect: rows before
    the fetched seed are outside the window and cannot be anchored.
    """

    rows = _rewritten_chain()
    result = verify_windowed_chain(rows[1:], predecessor=rows[0], predecessor_is_chain_head=False)
    assert result.ok is True
    assert result.rows_checked == 2
