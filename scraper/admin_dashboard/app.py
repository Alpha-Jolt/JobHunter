"""Admin dashboard FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from scraper.config import config
from scraper.logging_.metrics import Metrics
from admin_dashboard.routes import router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.use_database:
        from scraper.db.connection import init_db, dispose_db
        init_db(config.database_url, pool_size=config.db_pool_size)
    yield
    if config.use_database:
        await dispose_db()

app = FastAPI(title="JobHunter Admin Dashboard", lifespan=lifespan)

_STATIC = Path(__file__).parent / "static"
if _STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    template = Path(__file__).parent / "templates" / "dashboard.html"
    return HTMLResponse(template.read_text(encoding="utf-8"))


@app.get("/metrics", response_class=HTMLResponse)
async def prometheus_metrics() -> HTMLResponse:
    return HTMLResponse(Metrics.prometheus_text(), media_type="text/plain")
