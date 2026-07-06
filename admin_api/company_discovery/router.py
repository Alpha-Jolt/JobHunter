"""Company discovery and career jobs router for the Admin API.

Replaces the previous HTTP proxy. Writes directly to Redis (task queue)
and PostgreSQL (audit log + read queries). All endpoints require an active
admin session.
"""

import logging
from typing import Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_admin_session
from core.db import get_db
from core.redis import get_redis
from company_discovery.models import (
    BootstrapRequest,
    StartCareerScrapeRequest,
    StartDiscoveryRequest,
)
from company_discovery import service

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_admin_session)])


# ── Company Discovery ─────────────────────────────────────────────────────────

@router.post("/company-discovery/start")
async def start_discovery(
    body: StartDiscoveryRequest,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    """Trigger keyword-driven company discovery."""
    from datetime import datetime, timezone

    payload = {
        "role": body.role,
        "location": body.location,
        "experience": body.experience,
        "salary": body.salary,
    }
    run_id = await service.create_run_and_enqueue(
        db=db,
        r=r,
        task_type="search_discovery",
        source=f"{body.role} {body.location}",
        payload=payload,
    )
    return {
        "run_id": run_id,
        "status": "queued",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/company-discovery/bootstrap")
async def run_bootstrap(
    body: BootstrapRequest,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    """Trigger bootstrap source import."""
    from datetime import datetime, timezone

    payload = {"sources": body.sources}
    run_id = await service.create_run_and_enqueue(
        db=db,
        r=r,
        task_type="company_discovery_bootstrap",
        source="bootstrap",
        payload=payload,
    )
    return {
        "run_id": run_id,
        "status": "queued",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/company-discovery/status/{run_id}")
async def get_discovery_status(
    run_id: str,
    r: redis.Redis = Depends(get_redis),
):
    """Return status for a discovery run."""
    status = await service.get_run_status(run_id, r)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return status


@router.get("/company-discovery/companies")
async def list_companies(
    crawl_status: Optional[str] = Query(default=None),
    ats_platform: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated company list."""
    companies, total = await service.get_companies(
        db=db,
        crawl_status=crawl_status,
        ats_platform=ats_platform,
        limit=limit,
        offset=offset,
    )
    return {"companies": companies, "total": total, "limit": limit, "offset": offset}


@router.get("/company-discovery/stats")
async def get_company_stats(
    db: AsyncSession = Depends(get_db),
):
    """Return company enrichment statistics."""
    return await service.get_company_stats(db)


# ── Career Jobs ───────────────────────────────────────────────────────────────

@router.post("/career-jobs/start")
async def start_career_scrape(
    body: StartCareerScrapeRequest,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    """Trigger a career page scrape run."""
    from datetime import datetime, timezone

    payload = {"company_id": str(body.company_id) if body.company_id else None}
    run_id = await service.create_run_and_enqueue(
        db=db,
        r=r,
        task_type="career_page_scrape",
        source="career_page_scrape",
        payload=payload,
    )
    return {
        "run_id": run_id,
        "status": "queued",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/career-jobs/status/{run_id}")
async def get_career_scrape_status(
    run_id: str,
    r: redis.Redis = Depends(get_redis),
):
    """Return status for a career scrape run."""
    status = await service.get_run_status(run_id, r)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return status


@router.get("/career-jobs/latest")
async def get_latest_career_jobs(
    company_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated active career jobs."""
    import uuid as _uuid

    if company_id is not None:
        try:
            _uuid.UUID(company_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid company_id UUID")

    jobs, total = await service.get_latest_jobs(
        db=db,
        company_id=company_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return {"jobs": jobs, "total": total, "limit": limit, "offset": offset}


@router.get("/career-jobs/counts")
async def get_career_job_counts(
    db: AsyncSession = Depends(get_db),
):
    """Return aggregated career job counts."""
    return await service.get_job_counts(db)
