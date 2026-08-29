"""Audit log Pydantic contract transcribed from docs/15 (exactly 15 action types)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class AuditActionType(str, Enum):
    SOURCE_ACCESSED = "source_accessed"
    RAW_ARCHIVED = "raw_archived"
    CONTENT_SANITIZED = "content_sanitized"
    FACT_EXTRACTED = "fact_extracted"
    FACT_VALIDATED = "fact_validated"
    GRAPH_UPDATED = "graph_updated"
    HYPOTHESIS_CREATED = "hypothesis_created"
    INSIGHT_PROMOTED = "insight_promoted"
    BELIEF_CREATED = "belief_created"
    BELIEF_CALIBRATED = "belief_calibrated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECIDED = "approval_decided"
    BUDGET_BREACHED = "budget_breached"
    SOURCE_QUARANTINED = "source_quarantined"
    CONFIG_CHANGED = "config_changed"


class AuditLogRecord(BaseModel):
    audit_id: UUID
    sequence_no: int
    occurred_at: datetime
    actor_type: Literal["agent", "user", "system"]
    actor_id: str
    action_type: AuditActionType
    target_object_type: str
    target_object_id: Optional[UUID]
    run_id: Optional[UUID]
    event_id: Optional[UUID]
    payload_hash_sha256: str
    payload_canonical_json: dict[str, Any]
    previous_row_hash_sha256: str
    row_hash_sha256: str
