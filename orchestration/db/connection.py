"""Async PostgreSQL engine and session factory for JobHunter orchestration."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

_engine = None
_async_session_factory: async_sessionmaker | None = None


def init_engine(database_url: str, pool_size: int = 10, max_overflow: int = 20) -> None:
    """Initialise the async engine and session factory.

    Args:
        database_url: asyncpg-compatible PostgreSQL URL.
        pool_size: Connection pool size.
        max_overflow: Max connections above pool_size.
    """
    global _engine, _async_session_factory
    _engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )
    _async_session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info("Database engine initialised")


async def dispose_engine() -> None:
    """Dispose the async engine on application shutdown."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database engine disposed")


async def validate_connection() -> bool:
    """Verify the database connection is reachable.

    Returns:
        True if the connection succeeds.

    Raises:
        Exception: If the connection fails.
    """
    if _engine is None:
        raise RuntimeError("Engine not initialised — call init_engine() first")
    async with _engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager yielding a database session.

    Yields:
        AsyncSession instance.
    """
    if _async_session_factory is None:
        raise RuntimeError("Session factory not initialised — call init_engine() first")
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_session_factory() -> async_sessionmaker:
    """Return the session factory for use in FastAPI dependencies.

    Returns:
        The async_sessionmaker instance.

    Raises:
        RuntimeError: If the engine has not been initialised.
    """
    if _async_session_factory is None:
        raise RuntimeError("Session factory not initialised — call init_engine() first")
    return _async_session_factory
