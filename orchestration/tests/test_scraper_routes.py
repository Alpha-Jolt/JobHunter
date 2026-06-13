"""Tests for scraper API routes using FastAPI TestClient."""

import uuid
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from orchestration.api.main import app
from orchestration.auth.tokens import encode_access_token as _encode
from orchestration.auth.models.user import RoleEnum as _RoleEnum, UserRecord as _UserRecord

_TEST_SECRET = "test-secret-key-that-is-32-chars!!"
_TEST_ALG = "HS256"


def _make_admin():
    return _UserRecord(
        user_id=uuid.uuid4(), email="admin@example.com",
        password_hash="hash", role=_RoleEnum.ADMIN,
    )


def _make_hunter():
    return _UserRecord(
        user_id=uuid.uuid4(), email="hunter@example.com",
        password_hash="hash", role=_RoleEnum.HUNTER,
    )


def _auth_headers(user=None):
    u = user or _make_admin()
    tok = _encode(str(u.user_id), u.role, _TEST_SECRET, _TEST_ALG,
                  _dt.now(_tz.utc) + _td(minutes=15))
    return {"Authorization": f"Bearer {tok}"}, u


def _patch_auth(user):
    return (
        patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_TEST_SECRET, _TEST_ALG)),
        patch("orchestration.auth.dependencies.AuthRepository"),
        patch("orchestration.auth.dependencies.get_session_factory"),
    )


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "JobHunter" in resp.json()["message"]


def test_scraper_unauthenticated_returns_401(client):
    resp = client.post("/api/scraper/start", json={
        "source": "naukri", "keywords": ["python"],
        "locations": ["Bangalore"], "pages": 1,
    })
    assert resp.status_code == 401


def test_scraper_hunter_role_returns_403(client):
    hunter = _make_hunter()
    headers, _ = _auth_headers(hunter)
    p1, p2, p3 = _patch_auth(hunter)
    with p1, p2 as MockRepo, p3:
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=hunter)
        MockRepo.return_value = repo_inst
        resp = client.get("/api/scraper/counts", headers=headers)
    assert resp.status_code == 403


def test_start_scraper_invalid_source(client):
    admin = _make_admin()
    headers, _ = _auth_headers(admin)
    p1, p2, p3 = _patch_auth(admin)
    with p1, p2 as MockRepo, p3, \
         patch("orchestration.api.routes.scraper.get_db_session"):
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=admin)
        MockRepo.return_value = repo_inst
        resp = client.post(
            "/api/scraper/start",
            json={"source": "unknown_source", "keywords": ["python"],
                  "locations": ["Bangalore"], "pages": 1},
            headers=headers,
        )
    assert resp.status_code == 422


def test_start_scraper_valid(client):
    admin = _make_admin()
    headers, _ = _auth_headers(admin)
    run_id = uuid.uuid4()
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    p1, p2, p3 = _patch_auth(admin)
    with p1, p2 as MockRepo, p3, \
         patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch("orchestration.services.scraper_service.ScraperService.trigger_scrape",
               new_callable=AsyncMock, return_value=run_id):
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=admin)
        MockRepo.return_value = repo_inst
        resp = client.post(
            "/api/scraper/start",
            json={"source": "naukri", "keywords": ["python"],
                  "locations": ["Bangalore"], "pages": 2},
            headers=headers,
        )
    assert resp.status_code == 201
    data = resp.json()
    assert "run_id" in data
    assert data["status"] == "queued"


def test_scraper_status_not_found(client):
    admin = _make_admin()
    headers, _ = _auth_headers(admin)
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    p1, p2, p3 = _patch_auth(admin)
    with p1, p2 as MockRepo, p3, \
         patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch("orchestration.services.scraper_service.ScraperService.get_scrape_status",
               new_callable=AsyncMock, return_value=None):
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=admin)
        MockRepo.return_value = repo_inst
        resp = client.get(f"/api/scraper/status/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


def test_latest_jobs(client):
    admin = _make_admin()
    headers, _ = _auth_headers(admin)
    mock_session = AsyncMock()

    async def fake_session():
        yield mock_session

    p1, p2, p3 = _patch_auth(admin)
    with p1, p2 as MockRepo, p3, \
         patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch("orchestration.services.scraper_service.ScraperService.get_latest_jobs",
               new_callable=AsyncMock, return_value=[]):
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=admin)
        MockRepo.return_value = repo_inst
        resp = client.get("/api/scraper/latest-jobs?limit=5&offset=0", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_job_counts(client):
    admin = _make_admin()
    headers, _ = _auth_headers(admin)
    mock_session = AsyncMock()
    counts = {
        "total_jobs": 10,
        "by_source": {"naukri": 5, "indeed": 5},
        "by_status": {"raw": 10},
        "by_email_trust": {"unknown": 10},
    }

    async def fake_session():
        yield mock_session

    p1, p2, p3 = _patch_auth(admin)
    with p1, p2 as MockRepo, p3, \
         patch("orchestration.api.routes.scraper.get_db_session", fake_session), \
         patch("orchestration.services.scraper_service.ScraperService.get_job_counts",
               new_callable=AsyncMock, return_value=counts):
        repo_inst = AsyncMock()
        repo_inst.get_user_by_id = AsyncMock(return_value=admin)
        MockRepo.return_value = repo_inst
        resp = client.get("/api/scraper/counts", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_jobs"] == 10
