"""Company discovery service — manages discovery runs and company inventory queries."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import orchestration.db.models as _db_models
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CompanyDiscoveryService:
    """High-level company discovery operations backed by PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def trigger_bootstrap(
        self, sources: Optional[List[str]] = None
    ) -> uuid.UUID:
        """Create a scraper_run record for a bootstrap import and return its run_id.

        Args:
            sources: List of source names to import, or None/['all'] for all sources.

        Returns:
            UUID of the created scraper_run record.
        """
        sources = sources or ["all"]
        run = _db_models.ScraperRun(
            run_id=str(uuid.uuid4()),
            source="company_discovery_bootstrap",
            keywords=sources,
            locations=[],
            pages_requested=1,
            status="queued",
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(run)
        await self._session.flush()
        return uuid.UUID(run.run_id)

    async def trigger_discovery(
        self,
        role: str,
        location: str,
        experience: str = "fresher",
        salary: Optional[str] = None,
    ) -> uuid.UUID:
        """Create a scraper_run record for a keyword search discovery run.

        Args:
            role: Role keyword (e.g. "python developer").
            location: Target location string.
            experience: "fresher", "intermediate", or "advanced".
            salary: Optional salary range string.

        Returns:
            UUID of the created scraper_run record.
        """
        keywords = [role]
        if salary:
            keywords.append(salary)
        run = _db_models.ScraperRun(
            run_id=str(uuid.uuid4()),
            source="company_discovery_search",
            keywords=keywords,
            locations=[location],
            pages_requested=1,
            status="queued",
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(run)
        await self._session.flush()
        return uuid.UUID(run.run_id)

    async def get_run_status(self, run_id: uuid.UUID) -> Optional[Dict]:
        """Return status dict for a discovery run.

        Args:
            run_id: UUID of the scraper_run record.

        Returns:
            Status dict or None if not found.
        """
        ScraperRun = _db_models.ScraperRun
        result = await self._session.execute(
            select(ScraperRun).where(ScraperRun.run_id == str(run_id))
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {
            "run_id": str(row.run_id),
            "source": row.source,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "status": row.status,
            "companies_found": row.jobs_inserted,
            "errors": row.errors,
            "error_detail": row.error_detail,
        }

    async def get_companies(
        self,
        crawl_status: Optional[str] = None,
        ats_platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        """Return paginated company records with optional filters.

        Args:
            crawl_status: Filter by crawl_status value.
            ats_platform: Filter by ats_platform value.
            limit: Page size.
            offset: Pagination offset.

        Returns:
            Tuple of (list of company dicts, total count).
        """
        Company = _db_models.Company
        base_stmt = select(Company)

        if crawl_status:
            base_stmt = base_stmt.where(Company.crawl_status == crawl_status)
        if ats_platform:
            base_stmt = base_stmt.where(Company.ats_platform == ats_platform)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = base_stmt.order_by(Company.discovery_date.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        companies = [_company_to_dict(row) for row in rows]
        return companies, total

    async def get_stats(self) -> Dict:
        """Return aggregated company stats: counts by crawl_status and ats_platform,
        plus email stats.

        Returns:
            Stats dict.
        """
        Company = _db_models.Company

        total = (await self._session.execute(
            select(func.count()).select_from(Company)
        )).scalar() or 0

        by_status = {
            r.crawl_status: r.cnt
            for r in (await self._session.execute(
                select(Company.crawl_status, func.count().label("cnt"))
                .group_by(Company.crawl_status)
            ))
        }

        by_ats = {
            r.ats_platform: r.cnt
            for r in (await self._session.execute(
                select(Company.ats_platform, func.count().label("cnt"))
                .group_by(Company.ats_platform)
            ))
        }

        # Count companies with at least one career email
        with_career_email = (await self._session.execute(
            select(func.count()).select_from(Company).where(
                func.cardinality(Company.career_emails) > 0
            )
        )).scalar() or 0

        # Count low-trust companies
        low_trust_count = (await self._session.execute(
            select(func.count()).select_from(Company).where(
                Company.email_trust == "low_trust"
            )
        )).scalar() or 0

        # Count companies with career page URL
        with_career_page = (await self._session.execute(
            select(func.count()).select_from(Company).where(
                Company.career_page_url.isnot(None)
            )
        )).scalar() or 0

        return {
            "total_companies": total,
            "by_crawl_status": by_status,
            "by_ats_platform": by_ats,
            "with_career_page_url": with_career_page,
            "with_career_email": with_career_email,
            "low_trust_email_count": low_trust_count,
        }


def _company_to_dict(row: _db_models.Company) -> Dict:
    """Convert a Company ORM row to a serialisable dict."""
    return {
        "company_id": str(row.company_id),
        "company_name": row.company_name,
        "apex_domain": row.apex_domain,
        "career_page_url": row.career_page_url,
        "career_emails": list(row.career_emails or []),
        "email_trust": row.email_trust,
        "ats_platform": row.ats_platform,
        "industry": row.industry,
        "hq_location": row.hq_location,
        "source": row.source,
        "crawl_status": row.crawl_status,
        "discovery_date": row.discovery_date.isoformat() if row.discovery_date else None,
        "last_enriched_at": row.last_enriched_at.isoformat() if row.last_enriched_at else None,
    }
