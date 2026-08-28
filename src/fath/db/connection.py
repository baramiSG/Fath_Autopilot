"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fath.config.settings import Settings


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine for the given database URL."""

    return create_async_engine(database_url)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to ``engine``."""

    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def engine_from_settings(settings: Settings) -> AsyncEngine:
    """Create an async engine from loaded application settings."""

    return create_engine(settings.database_url)


async def session_scope(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a session and close it after use."""

    session = factory()
    try:
        yield session
    finally:
        await session.close()
