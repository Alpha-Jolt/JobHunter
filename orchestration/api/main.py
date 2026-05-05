"""JobHunter Orchestration API — FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from orchestration.api.config import get_settings
from orchestration.api.middleware import (
    ErrorHandlingMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    add_cors,
)
from orchestration.api.routes import scraper as scraper_router
from orchestration.db.connection import dispose_engine, init_engine, validate_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JobHunter Orchestration API",
    description="Phase 0 — Scraper control, job inventory, and application pipeline.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware (order matters: first added = outermost) ──────────────────────
add_cors(app)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


# ── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    init_engine(
        settings.database.database_url,
        pool_size=settings.database.db_pool_size,
        max_overflow=settings.database.db_max_overflow,
    )
    logger.info("JobHunter Orchestration API started")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await dispose_engine()
    logger.info("JobHunter Orchestration API stopped")


# ── Core routes ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health() -> JSONResponse:
    """Liveness probe — always returns 200 if the process is running."""
    return JSONResponse({"status": "ok"})


@app.get("/readiness", tags=["system"])
async def readiness() -> JSONResponse:
    """Readiness probe — checks database connectivity."""
    try:
        await validate_connection()
        return JSONResponse({"status": "ok", "database": "connected"})
    except Exception as exc:
        logger.warning("Readiness check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "disconnected", "detail": str(exc)},
        )


@app.get("/", tags=["system"])
async def root() -> JSONResponse:
    """Welcome message."""
    return JSONResponse(
        {"message": "JobHunter Orchestration API", "docs": "/docs", "health": "/health"}
    )


# ── Feature routers ──────────────────────────────────────────────────────────
from orchestration.api.routes.ai import router as ai_router

app.include_router(scraper_router.router, prefix="/api", tags=["scraper"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
