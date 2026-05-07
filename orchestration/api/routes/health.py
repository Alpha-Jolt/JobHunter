"""Health check routes — /health and /readiness."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.dependencies import get_db_session, get_job_registry
from orchestration.repositories.postgres_job_repository import PostgresJobRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Liveness probe — always returns 200 if server is running."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "version": "0.1.0"}


@router.get("/readiness")
async def readiness_check(
    db_session: AsyncSession = Depends(get_db_session),
    job_registry: PostgresJobRepository = Depends(get_job_registry),
):
    """Readiness probe — returns 200 only if all dependencies are healthy."""
    checks = {}

    try:
        await db_session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        logger.error("database_check_failed", extra={"error": str(e)})
        checks["database"] = "down"

    try:
        await job_registry.count()
        checks["job_registry"] = "ok"
    except Exception as e:
        logger.error("job_registry_check_failed", extra={"error": str(e)})
        checks["job_registry"] = "down"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ok else "degraded",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
