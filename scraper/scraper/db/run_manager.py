"""ScraperRunManager — manages the lifecycle of scraper runs in the database."""

import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker

from scraper.db.models import ScraperRun
from scraper.logging_.logger import Logger

logger = Logger.get_logger(__name__)


class ScraperRunManager:
    """Manages the lifecycle of a scraper run record."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def create_run(
        self, source: str, keywords: List[str], locations: List[str], pages: int
    ) -> uuid.UUID:
        """Create a new 'running' scraper run."""
        run_id = uuid.uuid4()
        run = ScraperRun(
            run_id=run_id,
            source=source,
            keywords=keywords,
            locations=locations,
            pages_requested=pages,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        async with self._session_factory() as session:
            session.add(run)
            await session.commit()
        logger.info("Created scraper run", extra_data={"run_id": str(run_id)})
        return run_id

    async def mark_completed(self, run_id: uuid.UUID, fetched: int, inserted: int) -> None:
        """Mark a run as completed."""
        async with self._session_factory() as session:
            stmt = (
                update(ScraperRun)
                .where(ScraperRun.run_id == run_id)
                .values(
                    status="completed",
                    jobs_fetched=fetched,
                    jobs_inserted=inserted,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.execute(stmt)
            await session.commit()
        logger.info("Marked scraper run as completed", extra_data={"run_id": str(run_id)})

    async def mark_failed(self, run_id: uuid.UUID, errors: int, detail: str) -> None:
        """Mark a run as failed."""
        async with self._session_factory() as session:
            stmt = (
                update(ScraperRun)
                .where(ScraperRun.run_id == run_id)
                .values(
                    status="failed",
                    errors=errors,
                    error_detail=detail,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.execute(stmt)
            await session.commit()
        logger.info("Marked scraper run as failed", extra_data={"run_id": str(run_id)})
