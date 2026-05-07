"""PostgreSQL-backed ScraperRuns repository."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import orchestration.db.models as _m


class PostgresScraperRunsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest(self) -> Optional[_m.ScraperRun]:
        result = await self._session.execute(
            select(_m.ScraperRun).order_by(_m.ScraperRun.started_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_runs(self, limit: int = 10) -> List[_m.ScraperRun]:
        result = await self._session.execute(
            select(_m.ScraperRun).order_by(_m.ScraperRun.started_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
