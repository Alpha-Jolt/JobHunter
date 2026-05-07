"""Admin dashboard API routes."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.dependencies import (
    get_db_session,
    get_job_registry,
    get_scraper_runs_repo,
)
from orchestration.repositories.postgres_job_repository import PostgresJobRepository
from orchestration.repositories.postgres_scraper_runs_repository import (
    PostgresScraperRunsRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard/metrics")
async def get_metrics(
    session: AsyncSession = Depends(get_db_session),
    job_registry: PostgresJobRepository = Depends(get_job_registry),
    scraper_runs_repo: PostgresScraperRunsRepository = Depends(get_scraper_runs_repo),
):
    """Real-time metrics for the admin dashboard."""
    try:
        import orchestration.db.models as _m

        total_jobs = await job_registry.count()

        jobs_by_source = {}
        for source in ("linkedin", "naukri", "indeed"):
            jobs_by_source[source] = len(await job_registry.get_by_source(source))

        result = await session.execute(
            select(func.count()).select_from(_m.ResumeVariant)
        )
        total_variants = result.scalar() or 0

        result = await session.execute(
            select(func.count()).select_from(_m.ResumeVariant)
            .where(_m.ResumeVariant.approval_status == "pending")
        )
        pending_variants = result.scalar() or 0

        result = await session.execute(
            select(func.count()).select_from(_m.ApplicationLog)
        )
        total_applications = result.scalar() or 0

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await session.execute(
            select(func.count()).select_from(_m.ApplicationLog)
            .where(_m.ApplicationLog.sent_at >= cutoff)
        )
        sent_today = result.scalar() or 0

        last_run = await scraper_runs_repo.get_latest()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "jobs": {"total": total_jobs, "by_source": jobs_by_source},
            "variants": {
                "total": total_variants,
                "pending": pending_variants,
                "approved": total_variants - pending_variants,
            },
            "applications": {"total": total_applications, "sent_today": sent_today},
            "scraper": {
                "last_run": last_run.started_at.isoformat() if last_run else None,
                "last_status": last_run.status if last_run else "never",
            },
        }
    except Exception as e:
        logger.error("metrics_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")


@router.get("/variants-pending")
async def get_pending_variants(
    session: AsyncSession = Depends(get_db_session),
):
    """Get all variants awaiting approval."""
    try:
        import orchestration.db.models as _m

        result = await session.execute(
            select(_m.ResumeVariant)
            .where(_m.ResumeVariant.approval_status == "pending")
            .order_by(_m.ResumeVariant.created_at.desc())
        )
        variants = result.scalars().all()

        return {
            "count": len(variants),
            "variants": [
                {
                    "variant_id": str(v.variant_id),
                    "user_id": v.user_id,
                    "job_id": str(v.job_id),
                    "created_at": v.created_at.isoformat(),
                    "approval_token": v.approval_token,
                }
                for v in variants
            ],
        }
    except Exception as e:
        logger.error("pending_variants_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch pending variants")


@router.get("/applications-log")
async def get_applications_log(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session),
):
    """Get recent applications (paginated)."""
    try:
        import orchestration.db.models as _m

        count_result = await session.execute(
            select(func.count()).select_from(_m.ApplicationLog)
        )
        total = count_result.scalar() or 0

        result = await session.execute(
            select(_m.ApplicationLog)
            .order_by(_m.ApplicationLog.sent_at.desc())
            .offset(skip)
            .limit(limit)
        )
        apps = result.scalars().all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "applications": [
                {
                    "application_id": str(a.application_id),
                    "user_id": a.user_id,
                    "job_id": str(a.job_id),
                    "status": a.status,
                    "sent_at": a.sent_at.isoformat(),
                    "reply_count": a.reply_count,
                }
                for a in apps
            ],
        }
    except Exception as e:
        logger.error("applications_log_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch applications")


@router.get("/scraper-runs")
async def get_scraper_runs(
    limit: int = 10,
    scraper_runs_repo: PostgresScraperRunsRepository = Depends(get_scraper_runs_repo),
):
    """Get recent scraper runs."""
    try:
        runs = await scraper_runs_repo.get_latest_runs(limit)
        return {
            "count": len(runs),
            "runs": [
                {
                    "run_id": str(r.run_id),
                    "source": r.source,
                    "started_at": r.started_at.isoformat(),
                    "completed_at": (
                        r.completed_at.isoformat() if r.completed_at else None
                    ),
                    "duration_seconds": (
                        (r.completed_at - r.started_at).total_seconds()
                        if r.completed_at else None
                    ),
                    "records_fetched": r.jobs_fetched,
                    "records_inserted": r.jobs_inserted,
                    "error_count": r.errors,
                    "status": r.status,
                }
                for r in runs
            ],
        }
    except Exception as e:
        logger.error("scraper_runs_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch scraper runs")
