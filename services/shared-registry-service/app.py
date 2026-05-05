"""FastAPI application entry point."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from dependencies import setup_dependencies
from middleware import add_middleware
from routes import applications, files, health, jobs, variants

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Shared Registry Service",
        description="REST API wrapper for JobHunter shared/ library",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_middleware(app)
    setup_dependencies(app)

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(variants.router, prefix="/api/variants", tags=["variants"])
    app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
    app.include_router(files.router, prefix="/api/files", tags=["files"])

    logger.info("app_created", env=settings.api_env)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development",
    )
