"""A6 SourceRegistryRecord contract tests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from fath.db.models.source_registry import (
    AccessMethod,
    AuthRequirement,
    RobotsStatus,
    SourceClass,
    SourceRegistryRecord,
    SourceReliabilityTier,
    SourceStatus,
)

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

DOC03_AND_STATUS_DEFAULTS: dict[str, Any] = {
    "api_base_url": None,
    "robots_url": None,
    "terms_url": None,
    "auth_requirement": AuthRequirement.NONE,
    "subscription_name": None,
    "allowed_paths": [],
    "disallowed_paths": [],
    "robots_status": RobotsStatus.UNKNOWN,
    "max_requests_per_minute": 30,
    "max_pages_per_cycle": 200,
    "max_bytes_per_cycle": 500_000_000,
    "language_codes": ["en"],
    "country_scope": [],
    "topic_scope": [],
    "update_frequency_hint": "unknown",
    "independence_group": None,
    "reliability_prior": 0.70,
    "strategic_relevance_score": 0.50,
    "data_quality_notes": None,
    "legal_notes": None,
    "enabled": True,
    "last_access_review_at": None,
    "metadata": {},
    "status": SourceStatus.CANDIDATE,
}

DEFAULT_MUTATIONS: dict[str, Any] = {
    "api_base_url": "https://example.net/api",
    "robots_url": "https://example.net/robots.txt",
    "terms_url": "https://example.net/terms",
    "auth_requirement": AuthRequirement.API_KEY,
    "subscription_name": "unexpected-default",
    "allowed_paths": ["/unexpected"],
    "disallowed_paths": ["/unexpected"],
    "robots_status": RobotsStatus.ALLOWED,
    "max_requests_per_minute": 0,
    "max_pages_per_cycle": 0,
    "max_bytes_per_cycle": 0,
    "language_codes": ["fr"],
    "country_scope": ["XX"],
    "topic_scope": ["unexpected"],
    "update_frequency_hint": "daily",
    "independence_group": "unexpected-default",
    "reliability_prior": 0.0,
    "strategic_relevance_score": 0.0,
    "data_quality_notes": "unexpected-default",
    "legal_notes": "unexpected-default",
    "enabled": False,
    "last_access_review_at": NOW,
    "metadata": {"unexpected": "default"},
    "status": SourceStatus.ACTIVE,
}


def _minimal(**overrides: object) -> SourceRegistryRecord:
    payload: dict[str, object] = {
        "slug": "synthetic_alpha",
        "name": "Synthetic Alpha",
        "source_class": SourceClass.GLOBAL_INDICATOR,
        "reliability_tier": SourceReliabilityTier.INSTITUTIONAL,
        "base_url": "https://example.com/registry",
        "access_method": AccessMethod.API,
        "created_at": NOW,
        "updated_at": NOW,
    }
    payload.update(overrides)
    return SourceRegistryRecord.model_validate(payload)


def _assert_all_defaults(record: SourceRegistryRecord) -> None:
    for field, expected in DOC03_AND_STATUS_DEFAULTS.items():
        actual = getattr(record, field)
        assert actual == expected, (field, actual, expected)


def test_golden_positive_validates() -> None:
    record = _minimal()
    assert record.slug == "synthetic_alpha"
    assert record.status is SourceStatus.CANDIDATE


def test_doc03_field_defaults() -> None:
    record = _minimal()
    _assert_all_defaults(record)
    assert isinstance(record.source_id, UUID)
    other = _minimal()
    assert record.source_id != other.source_id


@pytest.mark.parametrize("field", sorted(DEFAULT_MUTATIONS))
def test_altered_default_fails_oracle(field: str) -> None:
    assert set(DEFAULT_MUTATIONS) == set(DOC03_AND_STATUS_DEFAULTS)
    record = _minimal()
    object.__setattr__(record, field, DEFAULT_MUTATIONS[field])
    with pytest.raises(AssertionError):
        _assert_all_defaults(record)


def test_missing_required_field_rejected() -> None:
    payload = {
        "slug": "synthetic_alpha",
        "source_class": SourceClass.GLOBAL_INDICATOR,
        "reliability_tier": SourceReliabilityTier.INSTITUTIONAL,
        "base_url": "https://example.com/registry",
        "access_method": AccessMethod.API,
        "created_at": NOW,
        "updated_at": NOW,
    }
    with pytest.raises(ValidationError):
        SourceRegistryRecord.model_validate(payload)


def test_null_required_name_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal(name=None)


def test_invalid_enum_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal(source_class="not_a_class")


def test_invalid_url_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal(base_url="not-a-url")


def test_invalid_status_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal(status="bogus")


def test_missing_slug_rejected() -> None:
    payload = {
        "name": "Synthetic Beta",
        "source_class": SourceClass.GLOBAL_INDICATOR,
        "reliability_tier": SourceReliabilityTier.INSTITUTIONAL,
        "base_url": "https://example.net/registry",
        "access_method": AccessMethod.API,
        "created_at": NOW,
        "updated_at": NOW,
    }
    with pytest.raises(ValidationError):
        SourceRegistryRecord.model_validate(payload)


@pytest.mark.parametrize("value", [0, 1])
def test_reliability_prior_accepts_bounds(value: float) -> None:
    record = _minimal(reliability_prior=value)
    assert record.reliability_prior == value


@pytest.mark.parametrize("value", [-0.001, 1.001])
def test_reliability_prior_rejects_outside(value: float) -> None:
    with pytest.raises(ValidationError):
        _minimal(reliability_prior=value)


@pytest.mark.parametrize("value", [0, 1])
def test_strategic_relevance_accepts_bounds(value: float) -> None:
    record = _minimal(strategic_relevance_score=value)
    assert record.strategic_relevance_score == value


@pytest.mark.parametrize("value", [-0.001, 1.001])
def test_strategic_relevance_rejects_outside(value: float) -> None:
    with pytest.raises(ValidationError):
        _minimal(strategic_relevance_score=value)


def test_conint_accepts_zero() -> None:
    record = _minimal(max_requests_per_minute=0, max_pages_per_cycle=0, max_bytes_per_cycle=0)
    assert record.max_requests_per_minute == 0
    assert record.max_pages_per_cycle == 0
    assert record.max_bytes_per_cycle == 0


def test_conint_rejects_negative() -> None:
    with pytest.raises(ValidationError):
        _minimal(max_requests_per_minute=-1)
    with pytest.raises(ValidationError):
        _minimal(max_pages_per_cycle=-1)
    with pytest.raises(ValidationError):
        _minimal(max_bytes_per_cycle=-1)
