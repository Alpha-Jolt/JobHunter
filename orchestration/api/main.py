"""JobHunter Orchestration API — FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from orchestration.api.config import get_settings
from orchestration.api.middleware import (
    ErrorHandlingMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    add_cors,
)
from orchestration.api.routes import scraper as scraper_router
from orchestration.api.routes.ai import router as ai_router
from orchestration.api.routes.mail import router as mail_router
from orchestration.api.routes.admin import router as admin_router
from orchestration.api.routes.health import router as health_router
from orchestration.auth.routes.auth import router as auth_router
from orchestration.api.routes.resume import router as resume_router
from orchestration.auth.middleware import JWTLoggingMiddleware
from orchestration.core.logging_setup import setup_logging
from orchestration.db.connection import dispose_engine, init_engine

settings = get_settings()
setup_logging(log_level=settings.api.log_level, log_format="json")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="JobHunter Orchestration API",
    description="Phase 0 — Scraper control, job inventory, and application pipeline.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ───────────────────────────────────────────────────────────────
add_cors(app)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(JWTLoggingMiddleware)


# ── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    init_engine(
        settings.database.database_url,
        pool_size=settings.database.db_pool_size,
        max_overflow=settings.database.db_max_overflow,
    )
    from orchestration.db.connection import _engine
    from orchestration.db.models import Base
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs("logs", exist_ok=True)
    logger.info("JobHunter Orchestration API started")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await dispose_engine()
    logger.info("JobHunter Orchestration API stopped")


# ── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["system"])
async def root() -> JSONResponse:
    """Welcome message."""
    return JSONResponse(
        {"message": "JobHunter Orchestration API", "docs": "/docs", "health": "/health"}
    )


# ── Feature routers ──────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
app.include_router(scraper_router.router, prefix="/api", tags=["scraper"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(mail_router)
app.include_router(admin_router)

# ── Static files (admin dashboard) ──────────────────────────────────────────
_admin_dir = os.path.join(os.path.dirname(__file__), "..", "static", "admin")
if os.path.isdir(_admin_dir):
    app.mount("/admin", StaticFiles(directory=_admin_dir, html=True), name="admin")
