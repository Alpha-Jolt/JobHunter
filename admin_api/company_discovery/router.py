"""Company discovery and career jobs proxy router for the Admin API.

Forwards requests to the Orchestration API and returns responses.
All endpoints require an active admin session.
"""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from auth.dependencies import require_admin_session
from core.config import settings
from company_discovery.models import (
    BootstrapRequest,
    StartCareerScrapeRequest,
    StartDiscoveryRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_admin_session)])

# Base URL of the Orchestration API (same network, no auth header needed
# because admin_api already validates the session before forwarding)
_ORCH_BASE = getattr(settings, "ORCHESTRATION_API_URL", "http://orchestration:8000")
_TIMEOUT = 30.0


async def _forward(
    method: str,
    path: str,
    token: str,
    **kwargs,
) -> dict:
    """Forward a request to the Orchestration API.

    Args:
        method: HTTP method string.
        path: API path (without base URL).
        token: Bearer token to forward for RBAC.
        **kwargs: Additional arguments passed to httpx request.

    Returns:
        Parsed JSON response dict.

    Raises:
        HTTPException: On non-2xx response or network error.
    """
    url = f"{_ORCH_BASE}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await getattr(client, method)(url, headers=headers, **kwargs)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Orchestration API forward failed", exc_info=exc)
        raise HTTPException(status_code=502, detail="Orchestration API unreachable")


def _get_token(request: Request) -> str:
    """Extract Bearer token from the incoming request."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return ""


# ── Company Discovery ─────────────────────────────────────────────────────────

@router.post("/company-discovery/start")
async def start_discovery(body: StartDiscoveryRequest, request: Request):
    """Trigger keyword-driven company discovery."""
    return await _forward("post", "/api/company-discovery/start", _get_token(request), json=body.model_dump())


@router.post("/company-discovery/bootstrap")
async def run_bootstrap(body: BootstrapRequest, request: Request):
    """Trigger bootstrap source import."""
    return await _forward("post", "/api/company-discovery/bootstrap", _get_token(request), json=body.model_dump())


@router.get("/company-discovery/status/{run_id}")
async def get_discovery_status(run_id: str, request: Request):
    """Return status for a discovery run."""
    return await _forward("get", f"/api/company-discovery/status/{run_id}", _get_token(request))


@router.get("/company-discovery/companies")
async def list_companies(
    request: Request,
    crawl_status: Optional[str] = Query(default=None),
    ats_platform: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated company list."""
    params = {"limit": limit, "offset": offset}
    if crawl_status:
        params["crawl_status"] = crawl_status
    if ats_platform:
        params["ats_platform"] = ats_platform
    return await _forward("get", "/api/company-discovery/companies", _get_token(request), params=params)


@router.get("/company-discovery/stats")
async def get_company_stats(request: Request):
    """Return company enrichment statistics."""
    return await _forward("get", "/api/company-discovery/stats", _get_token(request))


# ── Career Jobs ───────────────────────────────────────────────────────────────

@router.post("/career-jobs/start")
async def start_career_scrape(body: StartCareerScrapeRequest, request: Request):
    """Trigger a career page scrape run."""
    return await _forward("post", "/api/career-jobs/start", _get_token(request), json=body.model_dump())


@router.get("/career-jobs/status/{run_id}")
async def get_career_scrape_status(run_id: str, request: Request):
    """Return status for a career scrape run."""
    return await _forward("get", f"/api/career-jobs/status/{run_id}", _get_token(request))


@router.get("/career-jobs/latest")
async def get_latest_career_jobs(
    request: Request,
    company_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated active career jobs."""
    params = {"limit": limit, "offset": offset}
    if company_id:
        params["company_id"] = company_id
    if status:
        params["status"] = status
    return await _forward("get", "/api/career-jobs/latest", _get_token(request), params=params)


@router.get("/career-jobs/counts")
async def get_career_job_counts(request: Request):
    """Return aggregated career job counts."""
    return await _forward("get", "/api/career-jobs/counts", _get_token(request))
