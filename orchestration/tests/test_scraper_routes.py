"""Tests for scraper API routes using FastAPI TestClient."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from orchestration.api.main import app


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "JobHunter" in resp.json()["message"]


def test_start_scraper_invalid_source(client):
    with patch("orchestration.api.routes.scraper.get_db_session"):
        resp = client.post(
            "/api/scraper/start",
            json={
                "source": "unknown_source", "keywords": ["python"],
                "locations": ["Bangalore"], "pages": 1,
            },
        )
    assert resp.status_code == 422


def test_start_scraper_valid(client):
    mock_session = AsyncMock()
    run_id = uuid.uuid4()

    async def fake_session():
        yield mock_session

    with patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch(
             "orchestration.services.scraper_service.ScraperService.trigger_scrape",
             new_callable=AsyncMock,
             return_value=run_id,
         ):
        resp = client.post(
            "/api/scraper/start",
            json={
                "source": "naukri", "keywords": ["python"],
                "locations": ["Bangalore"], "pages": 2,
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert "run_id" in data
    assert data["status"] == "queued"


def test_scraper_status_not_found(client):
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    with patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch(
             "orchestration.services.scraper_service.ScraperService.get_scrape_status",
             new_callable=AsyncMock,
             return_value=None,
         ):
        resp = client.get(f"/api/scraper/status/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_latest_jobs(client):
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    with patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch(
             "orchestration.services.scraper_service.ScraperService.get_latest_jobs",
             new_callable=AsyncMock,
             return_value=[],
         ):
        resp = client.get("/api/scraper/latest-jobs?limit=5&offset=0")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_job_counts(client):
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    counts = {
        "total_jobs": 10,
        "by_source": {"naukri": 5, "indeed": 5},
        "by_status": {"raw": 10},
        "by_email_trust": {"unknown": 10},
    }
    with patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch(
             "orchestration.services.scraper_service.ScraperService.get_job_counts",
             new_callable=AsyncMock,
             return_value=counts,
         ):
        resp = client.get("/api/scraper/counts")
    assert resp.status_code == 200
    assert resp.json()["total_jobs"] == 10
