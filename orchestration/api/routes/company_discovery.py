"""Company discovery API routes — /api/company-discovery/*"""

import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.dependencies import get_db_session
from orchestration.auth.dependencies import require_role
from orchestration.auth.models.user import RoleEnum
from orchestration.services.company_discovery_service import CompanyDiscoveryService

router = APIRouter(prefix="/api/company-discovery", tags=["company-discovery"])


# ── Request / Response schemas ───────────────────────────────────────────────

class StartDiscoveryRequest(BaseModel):
    role: str = Field(..., description="Role keyword, e.g. 'python developer'")
    location: str = Field(..., description="Target location, e.g. 'Bangalore'")
    experience: str = Field(default="fresher", description="fresher | intermediate | advanced")
    salary: Optional[str] = Field(default=None, description="Optional salary range hint")


class BootstrapRequest(BaseModel):
    sources: List[str] = Field(
        default=["all"],
        description="Source list: 'all', 'datasets', 'vc_portfolio', 'github', 'directory'",
    )


class DiscoveryRunResponse(BaseModel):
    run_id: str
    status: str
    started_at: str


class DiscoveryStatusResponse(BaseModel):
    run_id: str
    source: str
    started_at: Optional[str]
    completed_at: Optional[str]
    status: str
    companies_found: int
    errors: int
    error_detail: Optional[str]


class CompanyResponse(BaseModel):
    company_id: str
    company_name: Optional[str]
    apex_domain: str
    career_page_url: Optional[str]
    career_emails: List[str]
    email_trust: str
    ats_platform: str
    industry: Optional[str]
    hq_location: Optional[str]
    source: str
    crawl_status: str
    discovery_date: Optional[str]
    last_enriched_at: Optional[str]


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
    total: int
    limit: int
    offset: int


class CompanyStatsResponse(BaseModel):
    total_companies: int
    by_crawl_status: Dict[str, int]
    by_ats_platform: Dict[str, int]
    with_career_page_url: int
    with_career_email: int
    low_trust_email_count: int


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=DiscoveryRunResponse,
    status_code=201,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def start_discovery(
    body: StartDiscoveryRequest,
    session: AsyncSession = Depends(get_db_session),
) -> DiscoveryRunResponse:
    """Trigger an admin-initiated keyword-driven company discovery run.

    Queues a search discovery job using the role + location inputs.
    Returns the run_id for polling status.
    """
    from datetime import datetime, timezone

    service = CompanyDiscoveryService(session)
    run_id = await service.trigger_discovery(
        role=body.role,
        location=body.location,
        experience=body.experience,
        salary=body.salary,
    )
    return DiscoveryRunResponse(
        run_id=str(run_id),
        status="queued",
        started_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post(
    "/bootstrap",
    response_model=DiscoveryRunResponse,
    status_code=201,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def run_bootstrap(
    body: BootstrapRequest,
    session: AsyncSession = Depends(get_db_session),
) -> DiscoveryRunResponse:
    """Trigger a bootstrap source import run.

    Imports company domains from public datasets, VC portfolios,
    GitHub orgs, and public directories.
    """
    from datetime import datetime, timezone

    service = CompanyDiscoveryService(session)
    run_id = await service.trigger_bootstrap(sources=body.sources)
    return DiscoveryRunResponse(
        run_id=str(run_id),
        status="queued",
        started_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/status/{run_id}",
    response_model=DiscoveryStatusResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def get_discovery_status(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> DiscoveryStatusResponse:
    """Return status and company counts for a discovery run."""
    service = CompanyDiscoveryService(session)
    data = await service.get_run_status(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return DiscoveryStatusResponse(**data)


@router.get(
    "/companies",
    response_model=CompanyListResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def list_companies(
    crawl_status: Optional[str] = Query(
        default=None,
        description="Filter: pending | enriched | failed | robots_blocked | access_denied",
    ),
    ats_platform: Optional[str] = Query(
        default=None,
        description="Filter by ATS platform e.g. greenhouse, lever, ashby, custom",
    ),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> CompanyListResponse:
    """Return a paginated list of companies with optional filters."""
    service = CompanyDiscoveryService(session)
    companies, total = await service.get_companies(
        crawl_status=crawl_status,
        ats_platform=ats_platform,
        limit=limit,
        offset=offset,
    )
    return CompanyListResponse(
        companies=[CompanyResponse(**c) for c in companies],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/stats",
    response_model=CompanyStatsResponse,
    dependencies=[Depends(require_role(RoleEnum.ADMIN))],
)
async def get_company_stats(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyStatsResponse:
    """Return aggregated company enrichment statistics."""
    service = CompanyDiscoveryService(session)
    stats = await service.get_stats()
    return CompanyStatsResponse(**stats)
