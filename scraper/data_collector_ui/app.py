"""Data Collector UI — user questionnaire FastAPI app."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from data_collector_ui.routes import router

app = FastAPI(title="JobHunter Data Collector")

_STATIC = Path(__file__).parent / "static"
if _STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def questionnaire() -> HTMLResponse:
    template = Path(__file__).parent / "templates" / "questionnaire.html"
    return HTMLResponse(template.read_text(encoding="utf-8"))
