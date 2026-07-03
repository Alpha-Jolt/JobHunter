"""Career jobs API routes — /api/career-jobs/*"""

import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.dependencies import get_db_session
from orchestration.auth.dependencies import require_role
from orchestration.auth.models.user import RoleEnum
from orchestration.services.career_jobs_service import CareerJobsService

router = APIRouter(prefix="/api/career-jobs", tags=["career-jobs"])


# ── Request / Response schemas ───────────────────────────────────────────────

class StartCareerScrapeRequest(BaseModel):
    company_id: Optional[str] = Field(
        default=None,
        description="Scrape a single company by UUID. Omit to scrape all enriched companies.",
    )


class CareerScrapeRunResponse(BaseModel):
    run_id: str
    status: str
    started_at: str


class CareerScrapeStatusResponse(BaseModel):
    run_id: str
    source: str
    started_at: Optional[str]
    completed_at: Optional[str]
    status: str
    jobs_found: int
    errors: int
    error_detail: Optional[str]


class CareerJobResponse(BaseModel):
    career_job_id: str
    company_id: str
    company_name: Optional[str]
    apex_domain: Optional[str]
    job_title: str
    job_url: str
    location: Optional[str]
    remote_type: Optional[str]
    job_type: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    experience_min: Optional[int]
    experience_max: Optional[int]
    skills_required: List[str]
    apply_email: Optional[str]
    apply_url: Optional[str]
    ats_platform: Optional[str]
    extraction_method: str
    posted_at: Optional[str]
    scraped_at: Optional[str]
    last_seen_at: Optional[str]
    status: str
    source_channel: str


class CareerJobsListResponse(BaseModel):
    jobs: List[CareerJobResponse]
    total: int
    limit: int
    offset: int


class CareerJobsCountsResponse(BaseModel):
    total_jobs: int
    by_status: Dict[str, int]
    by_extraction_method: Dict[str, int]
    active_companies_count: int
    jobs_with_apply_contact: int


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=CareerScrapeRunResponse,
    status_code=201,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def start_career_scrape(
    body: StartCareerScrapeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CareerScrapeRunResponse:
    """Trigger a career page job scrape run.

    If company_id is provided, scrapes only that company.
    Otherwise scrapes all enriched companies in the companies table.
    """
    from datetime import datetime, timezone

    company_uuid: Optional[uuid.UUID] = None
    if body.company_id:
        try:
            company_uuid = uuid.UUID(body.company_id)
        except ValueError:
            raise HTTPException(
                status_code=422, detail=f"Invalid company_id UUID: {body.company_id}"
            )

    service = CareerJobsService(session)
    run_id = await service.trigger_scrape(company_id=company_uuid)
    return CareerScrapeRunResponse(
        run_id=str(run_id),
        status="queued",
        started_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/status/{run_id}",
    response_model=CareerScrapeStatusResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def get_career_scrape_status(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> CareerScrapeStatusResponse:
    """Return status and job counts for a career page scrape run."""
    service = CareerJobsService(session)
    data = await service.get_run_status(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return CareerScrapeStatusResponse(**data)


@router.get(
    "/latest",
    response_model=CareerJobsListResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN, RoleEnum.HUNTER))],
)
async def get_latest_career_jobs(
    company_id: Optional[str] = Query(
        default=None, description="Filter by company UUID"
    ),
    status: Optional[str] = Query(
        default=None, description="Filter by status: active | closed | raw"
    ),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> CareerJobsListResponse:
    """Return paginated active career page jobs ordered by last_seen_at DESC."""
    company_uuid: Optional[uuid.UUID] = None
    if company_id:
        try:
            company_uuid = uuid.UUID(company_id)
        except ValueError:
            raise HTTPException(
                status_code=422, detail=f"Invalid company_id UUID: {company_id}"
            )

    service = CareerJobsService(session)
    jobs, total = await service.get_latest_jobs(
        company_id=company_uuid,
        status=status,
        limit=limit,
        offset=offset,
    )
    return CareerJobsListResponse(
        jobs=[CareerJobResponse(**j) for j in jobs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/counts",
    response_model=CareerJobsCountsResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN, RoleEnum.HUNTER))],
)
async def get_career_job_counts(
    session: AsyncSession = Depends(get_db_session),
) -> CareerJobsCountsResponse:
    """Return aggregated career job counts by status, extraction method, and company."""
    service = CareerJobsService(session)
    counts = await service.get_counts()
    return CareerJobsCountsResponse(**counts)
