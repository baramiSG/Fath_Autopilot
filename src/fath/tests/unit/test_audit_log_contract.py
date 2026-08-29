"""AuditLogRecord + AuditActionType contract (docs/15; IO-1 fifteen members)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import get_args
from uuid import UUID

import pytest
from pydantic import ValidationError

from fath.db.models.audit_log import AuditActionType, AuditLogRecord

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
SYNTHETIC_UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

DOC15_ACTION_VALUES = (
    "source_accessed",
    "raw_archived",
    "content_sanitized",
    "fact_extracted",
    "fact_validated",
    "graph_updated",
    "hypothesis_created",
    "insight_promoted",
    "belief_created",
    "belief_calibrated",
    "approval_requested",
    "approval_decided",
    "budget_breached",
    "source_quarantined",
    "config_changed",
)


def test_exactly_fifteen_action_types_and_no_fact_inserted() -> None:
    assert issubclass(AuditActionType, str)
    assert issubclass(AuditActionType, Enum)
    values = tuple(member.value for member in AuditActionType)
    assert values == DOC15_ACTION_VALUES
    assert len(values) == 15
    assert "fact_inserted" not in values
    for value in DOC15_ACTION_VALUES:
        assert AuditActionType(value).value == value


def test_unknown_action_type_rejected() -> None:
    with pytest.raises(ValueError):
        AuditActionType("fact_inserted")
    with pytest.raises(ValidationError):
        _record(action_type="fact_inserted")


def test_actor_type_literal() -> None:
    field = AuditLogRecord.model_fields["actor_type"]
    assert get_args(field.annotation) == ("agent", "user", "system")
    with pytest.raises(ValidationError):
        _record(actor_type="service")


def test_target_object_id_optional_uuid() -> None:
    row = _record(target_object_id=None)
    assert row.target_object_id is None
    row2 = _record(target_object_id=SYNTHETIC_UUID)
    assert row2.target_object_id == SYNTHETIC_UUID
    with pytest.raises(ValidationError):
        _record(target_object_id="synthetic_slug")


def test_fourteen_field_names() -> None:
    assert list(AuditLogRecord.model_fields) == [
        "audit_id",
        "sequence_no",
        "occurred_at",
        "actor_type",
        "actor_id",
        "action_type",
        "target_object_type",
        "target_object_id",
        "run_id",
        "event_id",
        "payload_hash_sha256",
        "payload_canonical_json",
        "previous_row_hash_sha256",
        "row_hash_sha256",
    ]
    for name in (
        "actor_kind",
        "event_category",
        "event_type",
        "target_kind",
        "target_id",
    ):
        assert name not in AuditLogRecord.model_fields


def _record(**overrides: object) -> AuditLogRecord:
    payload: dict[str, object] = {
        "audit_id": SYNTHETIC_UUID,
        "sequence_no": 1,
        "occurred_at": NOW,
        "actor_type": "system",
        "actor_id": "synthetic_actor",
        "action_type": AuditActionType.CONFIG_CHANGED,
        "target_object_type": "synthetic_target",
        "target_object_id": None,
        "run_id": None,
        "event_id": None,
        "payload_hash_sha256": "0" * 64,
        "payload_canonical_json": {"synthetic": True},
        "previous_row_hash_sha256": "0" * 64,
        "row_hash_sha256": "a" * 64,
    }
    payload.update(overrides)
    return AuditLogRecord.model_validate(payload)
