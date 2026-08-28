"""Typed settings loading."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from fath.config.settings import Settings


def test_settings_loads_exactly_three_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://fath:fath@127.0.0.1:5432/fath")
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("FATH_ENV", "test")
    settings = Settings(_env_file=None)
    assert settings.database_url.endswith("/fath")
    assert settings.redis_url.startswith("redis://")
    assert settings.fath_env == "test"


def test_settings_forbids_extra_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://fath:fath@127.0.0.1:5432/fath")
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("FATH_ENV", "test")
    with pytest.raises(ValidationError):
        Settings.model_validate(
            {
                "database_url": "postgresql+asyncpg://fath:fath@127.0.0.1:5432/fath",
                "redis_url": "redis://127.0.0.1:6379/0",
                "fath_env": "test",
                "unexpected": "field",
            }
        )


def test_settings_requires_all_three(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("FATH_ENV", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
