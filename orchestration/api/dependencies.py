"""FastAPI dependency injection helpers."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.config import Settings, get_settings
from orchestration.db.connection import get_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for use in route handlers.

    Yields:
        AsyncSession instance.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_app_settings(settings: Settings = Depends(get_settings)) -> Settings:
    """Return the application settings.

    Args:
        settings: Injected Settings instance.

    Returns:
        Settings instance.
    """
    return settings
