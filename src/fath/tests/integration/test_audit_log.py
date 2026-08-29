"""Integration tests for append-only hash-chained audit_log (rollback-only)."""

from __future__ import annotations

import inspect
import os
import subprocess
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from fath.db.audit_hash import (
    GENESIS_PREVIOUS_ROW_HASH,
    PayloadEncodingError,
    compute_row_hash_sha256,
    verify_chain,
)
from fath.db.audit_repo import append_in_transaction, fetch_audit_rows, verify_recent_chain
from fath.db.connection import create_engine, create_session_factory
from fath.db.models.audit_log import AuditActionType
from fath.tests.conftest import REPO_ROOT, sync_database_url

pytestmark = pytest.mark.integration

ZERO_US = datetime(2026, 1, 1, tzinfo=timezone.utc)
WITH_US = datetime(2026, 1, 1, 12, 34, 56, 123456, tzinfo=timezone.utc)
SYNTHETIC_UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PAYLOAD = {"n": 1, "synthetic": True}


def _async_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql+asyncpg://fath:fath@127.0.0.1:55432/fath")


@pytest.fixture()
async def engine() -> AsyncIterator[AsyncEngine]:
    eng = create_engine(_async_url())
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture()
def factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(engine)


async def _append(session: AsyncSession, **overrides: object) -> Any:
    kwargs: dict[str, object] = {
        "actor_type": "system",
        "actor_id": "synthetic_actor",
        "action_type": AuditActionType.CONFIG_CHANGED,
        "target_object_type": "synthetic_target",
        "target_object_id": None,
        "payload": dict(PAYLOAD),
        "occurred_at": ZERO_US,
    }
    kwargs.update(overrides)
    return await append_in_transaction(session, **kwargs)  # type: ignore[arg-type]


def test_append_signature_uses_docs15_names() -> None:
    params = list(inspect.signature(append_in_transaction).parameters)
    assert params == [
        "session",
        "actor_type",
        "actor_id",
        "action_type",
        "target_object_type",
        "target_object_id",
        "payload",
        "run_id",
        "event_id",
        "occurred_at",
    ]
    for forbidden in ("actor_kind", "event_category", "event_type", "target_kind", "target_id"):
        assert forbidden not in params


def test_audit_modules_forbid_listeners_and_create_task() -> None:
    for rel in (
        "src/fath/db/audit_hash.py",
        "src/fath/db/audit_repo.py",
        "src/fath/db/models/audit_log.py",
        "src/fath/db/migrations/versions/0002_audit_log.py",
        "scripts/verify_audit_chain.py",
    ):
        text_src = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "event.listen" not in text_src
        assert "create_task" not in text_src
        assert "event_category" not in text_src


async def test_requires_open_transaction(factory: async_sessionmaker[AsyncSession]) -> None:
    session = factory()
    try:
        with pytest.raises(RuntimeError, match="open transaction"):
            await _append(session)
    finally:
        await session.close()


async def test_three_row_chain_and_property_recompute(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        first = await _append(session, action_type=AuditActionType.CONFIG_CHANGED)
        second = await _append(
            session,
            action_type=AuditActionType.SOURCE_ACCESSED,
            target_object_id=SYNTHETIC_UUID,
            payload={"synthetic": True, "kind": "source"},
        )
        third = await _append(
            session, actor_id="synthetic_actor_b", payload={"n": 2, "synthetic": True}
        )
        assert first.previous_row_hash_sha256 == GENESIS_PREVIOUS_ROW_HASH
        assert first.sequence_no < second.sequence_no < third.sequence_no
        rows = await fetch_audit_rows(session)
        result = verify_chain(rows)
        assert result.ok is True
        assert result.rows_checked == 3
        for row in rows:
            recomputed = compute_row_hash_sha256(
                previous_row_hash_sha256=row.previous_row_hash_sha256,
                payload=row.payload,
                actor_id=row.actor_id,
                action_type=row.action_type,
                target_object_id=row.target_object_id,
                occurred_at=row.occurred_at,
            )
            assert recomputed == row.row_hash_sha256
        assert second.target_object_id == SYNTHETIC_UUID
        assert second.action_type is AuditActionType.SOURCE_ACCESSED
    finally:
        await session.rollback()
        await session.close()


async def test_caller_rollback_drops_audit_row(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        await _append(session)
        rows = await fetch_audit_rows(session)
        assert len(rows) == 1
    finally:
        await session.rollback()
        await session.close()
    session = factory()
    try:
        leftover = await fetch_audit_rows(session)
        assert leftover == []
    finally:
        await session.close()


async def test_windowed_recent_verification_healthy_then_in_window_tamper(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    """K > W: CLI-equivalent windowed path passes on a healthy chain; in-window
    covered-field tamper is detected. Rollback-only (IO-9).
    """

    window = 3
    session = factory()
    await session.begin()
    try:
        records = [
            await _append(session, payload={"n": index, "synthetic": True}) for index in range(5)
        ]
        naive_window = verify_chain(await fetch_audit_rows(session, recent=window))
        assert naive_window.ok is False
        healthy = await verify_recent_chain(session, recent=window)
        assert healthy.ok is True
        assert healthy.rows_checked == window
        includes_head = await verify_recent_chain(session, recent=10)
        assert includes_head.ok is True
        assert includes_head.rows_checked == 5
        await session.execute(
            text("ALTER TABLE audit_log DISABLE TRIGGER trg_audit_log_append_only")
        )
        await session.execute(
            text("UPDATE audit_log SET actor_id = :actor WHERE audit_id = :audit_id"),
            {"actor": "mutated_actor", "audit_id": records[-1].audit_id},
        )
        tampered = await verify_recent_chain(session, recent=window)
        assert tampered.ok is False
        assert tampered.failure_reason is not None
    finally:
        await session.rollback()
        await session.close()


async def _rewrite_chain_from_anchor(session: AsyncSession, anchor: str) -> None:
    """Re-link every stored row from ``anchor``, keeping each row internally
    consistent so only the missing genesis anchor is detectable. Requires the
    append-only trigger to be disabled by the caller.
    """

    previous = anchor
    for row in await fetch_audit_rows(session):
        row_hash = compute_row_hash_sha256(
            previous_row_hash_sha256=previous,
            payload=row.payload,
            actor_id=row.actor_id,
            action_type=row.action_type,
            target_object_id=row.target_object_id,
            occurred_at=row.occurred_at,
        )
        await session.execute(
            text(
                "UPDATE audit_log SET previous_row_hash_sha256 = :previous,"
                " row_hash_sha256 = :row_hash WHERE sequence_no = :sequence_no"
            ),
            {"previous": previous, "row_hash": row_hash, "sequence_no": row.sequence_no},
        )
        previous = row_hash


async def test_window_reaching_chain_head_rejects_rewritten_anchor(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    """recent == K-1 fetches the chain head as the seed, so genesis must still be
    enforced there. Otherwise a chain rewritten from a forged anchor verifies
    clean at exactly that window size. Rollback-only (IO-9).
    """

    session = factory()
    await session.begin()
    try:
        for index in range(3):
            await _append(session, payload={"n": index, "synthetic": True})
        healthy = await verify_recent_chain(session, recent=2)
        assert healthy.ok is True
        assert healthy.rows_checked == 2

        await session.execute(
            text("ALTER TABLE audit_log DISABLE TRIGGER trg_audit_log_append_only")
        )
        await _rewrite_chain_from_anchor(session, "f" * 64)

        below_head = await verify_recent_chain(session, recent=1)
        assert below_head.ok is True
        assert below_head.rows_checked == 1

        reaching_head = await verify_recent_chain(session, recent=2)
        assert reaching_head.ok is False
        assert reaching_head.failure_reason is not None
        assert "not adjacent" in reaching_head.failure_reason
    finally:
        await session.rollback()
        await session.close()


async def test_windowed_verification_detects_tampered_seed_outside_window(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    """The seed row is recomputed, never trusted: a covered-field tamper on the
    row immediately before the window is detected even though every in-window
    row still recomputes cleanly. Rollback-only (IO-9).
    """

    window = 2
    session = factory()
    await session.begin()
    try:
        records = [
            await _append(session, payload={"n": index, "synthetic": True}) for index in range(4)
        ]
        assert (await verify_recent_chain(session, recent=window)).ok is True
        await session.execute(
            text("ALTER TABLE audit_log DISABLE TRIGGER trg_audit_log_append_only")
        )
        seed = records[1]
        await session.execute(
            text("UPDATE audit_log SET actor_id = :actor WHERE audit_id = :audit_id"),
            {"actor": "mutated_actor", "audit_id": seed.audit_id},
        )
        tampered = await verify_recent_chain(session, recent=window)
        assert tampered.ok is False
        assert tampered.failure_reason is not None
        assert f"sequence_no={seed.sequence_no}" in tampered.failure_reason
    finally:
        await session.rollback()
        await session.close()


async def test_verify_recent_chain_rejects_negative_window(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    """A negative window is a caller contract error, never an opaque IndexError."""

    session = factory()
    await session.begin()
    try:
        await _append(session)
        with pytest.raises(ValueError, match="non-negative"):
            await verify_recent_chain(session, recent=-1)
        zero = await verify_recent_chain(session, recent=0)
        assert zero.ok is True
        assert zero.rows_checked == 0
    finally:
        await session.rollback()
        await session.close()


async def test_gap_tolerant_after_nested_rollback(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        first = await _append(session)
        nested = await session.begin_nested()
        await _append(session, actor_id="synthetic_rolled_back")
        await nested.rollback()
        second = await _append(session, actor_id="synthetic_after_gap")
        assert second.sequence_no > first.sequence_no + 1
        rows = await fetch_audit_rows(session)
        assert [row.sequence_no for row in rows] == [first.sequence_no, second.sequence_no]
        result = verify_chain(rows)
        assert result.ok is True
        assert result.rows_checked == 2
    finally:
        await session.rollback()
        await session.close()


async def test_jsonb_stable_vectors_and_rejects(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        await _append(session, payload={"n": 1e-3, "synthetic": True})
        await _append(session, payload={"n": 2**53 + 1, "synthetic": True})
        await _append(session, payload={"ar": "مرحبا", "nested": {"a": [1, {"z": 2}]}})
        with pytest.raises(PayloadEncodingError):
            await _append(session, payload={"n": -0.0})
        with pytest.raises(PayloadEncodingError):
            await _append(session, payload={"n": 1e300})
        with pytest.raises(PayloadEncodingError):
            await _append(session, payload={"when": ZERO_US})
        rows = await fetch_audit_rows(session)
        assert verify_chain(rows).ok is True
    finally:
        await session.rollback()
        await session.close()


async def test_occurred_at_timestamptz_round_trip(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        zero = await _append(session, occurred_at=ZERO_US)
        micro = await _append(session, occurred_at=WITH_US)
        assert zero.occurred_at.isoformat() == "2026-01-01T00:00:00+00:00"
        assert micro.occurred_at.isoformat() == "2026-01-01T12:34:56.123456+00:00"
        rows = await fetch_audit_rows(session)
        assert verify_chain(rows).ok is True
    finally:
        await session.rollback()
        await session.close()


async def test_update_and_delete_raise(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        row = await _append(session)
        with pytest.raises(DBAPIError):
            await session.execute(
                text("UPDATE audit_log SET actor_id = :actor WHERE audit_id = :audit_id"),
                {"actor": "mutated_actor", "audit_id": row.audit_id},
            )
    finally:
        await session.rollback()
    await session.begin()
    try:
        row = await _append(session)
        with pytest.raises(DBAPIError):
            await session.execute(
                text("DELETE FROM audit_log WHERE audit_id = :audit_id"),
                {"audit_id": row.audit_id},
            )
    finally:
        await session.rollback()
        await session.close()


async def test_tamper_covered_field_with_trigger_disabled(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    """Mutate actor_id (hash-covered). Non-covered columns are trigger-only."""

    session = factory()
    await session.begin()
    try:
        row = await _append(session)
        await session.execute(
            text("ALTER TABLE audit_log DISABLE TRIGGER trg_audit_log_append_only")
        )
        await session.execute(
            text("UPDATE audit_log SET actor_id = :actor WHERE audit_id = :audit_id"),
            {"actor": "mutated_actor", "audit_id": row.audit_id},
        )
        stored = await fetch_audit_rows(session)
        result = verify_chain(stored)
        assert result.ok is False
    finally:
        await session.rollback()
        await session.close()


async def test_exclusive_lock_visible_to_second_connection(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    import psycopg

    session = factory()
    await session.begin()
    try:
        await _append(session)
        with psycopg.connect(sync_database_url()) as conn:
            locks = list(
                conn.execute(
                    """
                    SELECT 1
                    FROM pg_locks
                    JOIN pg_class ON pg_locks.relation = pg_class.oid
                    JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
                    WHERE pg_namespace.nspname = 'public'
                      AND pg_class.relname = 'audit_log'
                      AND pg_locks.mode = 'ExclusiveLock'
                    """
                )
            )
        assert locks
    finally:
        await session.rollback()
        await session.close()


async def test_fact_inserted_rejected_as_action_type(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    session = factory()
    await session.begin()
    try:
        with pytest.raises(ValueError):
            await _append(session, action_type="fact_inserted")
    finally:
        await session.rollback()
        await session.close()


def test_cli_recent_on_empty_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _async_url())
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:56379/0")
    monkeypatch.setenv("FATH_ENV", "test")
    completed = subprocess.run(
        ["uv", "run", "python", "scripts/verify_audit_chain.py", "--recent", "10000"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok rows_checked=0" in completed.stdout
