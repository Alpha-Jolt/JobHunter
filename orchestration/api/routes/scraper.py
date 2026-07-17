"""Scraper API routes — /api/scraper/*"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from orchestration.auth.dependencies import require_role
from orchestration.auth.models.user import RoleEnum
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.dependencies import get_db_session
from orchestration.services.scraper_service import ScraperService

router = APIRouter()


# ── Request / Response schemas ───────────────────────────────────────────────

class StartScraperRequest(BaseModel):
    source: str = Field(..., description="Job source: naukri or indeed")
    keywords: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    pages: int = Field(default=5, ge=1, le=50)


class StartScraperResponse(BaseModel):
    run_id: str
    started_at: str
    status: str


class ScraperStatusResponse(BaseModel):
    run_id: str
    source: str
    started_at: Optional[str]
    completed_at: Optional[str]
    status: str
    jobs_fetched: int
    jobs_inserted: int
    errors: int


class JobRecordResponse(BaseModel):
    job_id: str
    source: str
    title: str
    company_name: str
    location: Optional[str]
    description: str
    skills_required: List[str]
    apply_email: Optional[str]
    email_trust: str
    status: str
    last_seen_at: Optional[str]
    created_at: str


class LatestJobsResponse(BaseModel):
    jobs: List[JobRecordResponse]
    total: Optional[int] = None


class JobCountsResponse(BaseModel):
    total_jobs: int
    by_source: dict
    by_status: dict
    by_email_trust: dict


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/scraper/start", response_model=StartScraperResponse, status_code=201,
             dependencies=[Depends(require_role(RoleEnum.ADMIN))])
async def start_scraper(
    body: StartScraperRequest,
    session: AsyncSession = Depends(get_db_session),
) -> StartScraperResponse:
    """Trigger a new scraper run.

    Creates a scraper_run record and returns the run_id.
    Actual scraper invocation is a stub in Phase 0.
    """
    valid_sources = {"naukri", "indeed", "linkedin"}
    if body.source not in valid_sources:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid source '{body.source}'. Must be one of {sorted(valid_sources)}.",
        )

    service = ScraperService(session)
    run_id = await service.trigger_scrape(
        source=body.source,
        keywords=body.keywords,
        locations=body.locations,
        pages=body.pages,
    )
    from datetime import datetime, timezone

    return StartScraperResponse(
        run_id=str(run_id),
        started_at=datetime.now(timezone.utc).isoformat(),
        status="queued",
    )


@router.get("/scraper/status/{run_id}", response_model=ScraperStatusResponse,
            dependencies=[Depends(require_role(RoleEnum.ADMIN))])
async def get_scraper_status(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ScraperStatusResponse:
    """Return the status and aggregated counts for a scraper run."""
    service = ScraperService(session)
    data = await service.get_scrape_status(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Scraper run not found: {run_id}")
    return ScraperStatusResponse(**data)


@router.get("/scraper/latest-jobs", response_model=LatestJobsResponse,
            dependencies=[Depends(require_role(RoleEnum.ADMIN, RoleEnum.HUNTER))])
async def get_latest_jobs(
    source: Optional[str] = Query(default=None, description="Filter by source"),
    search: Optional[str] = Query(default=None, description="Search by title, company, or description"),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    include_career_jobs: bool = Query(default=False, description="Include career page jobs in results"),
    session: AsyncSession = Depends(get_db_session),
) -> LatestJobsResponse:
    """Return active jobs ordered by last_seen_at DESC with optional source filter and search."""
    service = ScraperService(session)
    jobs, total = await service.get_latest_jobs(source=source, limit=limit, offset=offset, search=search, include_career_jobs=include_career_jobs)

    job_responses = [
        JobRecordResponse(
            job_id=str(j.job_id),
            source=j.source,
            title=j.title,
            company_name=j.company_name,
            location=j.location,
            description=j.description or "",
            skills_required=j.skills_required or [],
            apply_email=j.apply_email,
            email_trust=j.email_trust,
            status=j.status,
            last_seen_at=j.last_seen_at.isoformat() if j.last_seen_at else None,
            created_at=(
                j.scraped_at.isoformat() if j.scraped_at
                else (j.posted_at.isoformat() if j.posted_at else "")
            )
        )
        for j in jobs
    ]
    return LatestJobsResponse(jobs=job_responses, total=total)


@router.get("/scraper/counts", response_model=JobCountsResponse,
            dependencies=[Depends(require_role(RoleEnum.ADMIN, RoleEnum.HUNTER))])
async def get_job_counts(
    session: AsyncSession = Depends(get_db_session),
) -> JobCountsResponse:
    """Return aggregated job counts by source, status, and email_trust."""
    service = ScraperService(session)
    counts = await service.get_job_counts()
    return JobCountsResponse(**counts)
