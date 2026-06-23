"""Async PostgreSQL engine and session factory for the scraper."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)

_engine = None
_async_session_factory: async_sessionmaker | None = None


def init_db(database_url: str, pool_size: int = 5, max_overflow: int = 10) -> None:
    """Initialise the async engine and session factory for the scraper."""
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
    logger.info("Scraper database engine initialised")


async def dispose_db() -> None:
    """Dispose the async engine on application shutdown."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Scraper database engine disposed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager yielding a database session."""
    if _async_session_factory is None:
        raise RuntimeError("Session factory not initialised — call init_db() first")
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_session_factory() -> async_sessionmaker:
    """Return the session factory."""
    if _async_session_factory is None:
        raise RuntimeError("Session factory not initialised — call init_db() first")
    return _async_session_factory
