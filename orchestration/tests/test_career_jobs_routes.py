"""Tests for /api/career-jobs/* routes using FastAPI TestClient.

Only GET /latest and GET /counts are tested here.
POST /start and GET /status/{run_id} have moved to admin_api.
"""

import uuid
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from orchestration.api.main import app
from orchestration.auth.models.user import RoleEnum as _RoleEnum, UserRecord as _UserRecord
from orchestration.auth.tokens import encode_access_token as _encode

_TEST_SECRET = "test-secret-key-that-is-32-chars!!"
_TEST_ALG = "HS256"

_FAKE_COMPANY_ID = str(uuid.uuid4())
_FAKE_JOB_ID = str(uuid.uuid4())

_SAMPLE_JOB = {
    "career_job_id": _FAKE_JOB_ID,
    "company_id": _FAKE_COMPANY_ID,
    "company_name": "Acme Corp",
    "apex_domain": "acme.com",
    "job_title": "Python Engineer",
    "job_url": "https://boards.greenhouse.io/acme/jobs/1",
    "location": "Bangalore",
    "remote_type": "hybrid",
    "job_type": "fulltime",
    "salary_min": 1000000,
    "salary_max": 1500000,
    "experience_min": 2,
    "experience_max": 5,
    "skills_required": ["python", "django"],
    "apply_email": "careers@acme.com",
    "apply_url": "https://boards.greenhouse.io/acme/jobs/1/apply",
    "ats_platform": "greenhouse",
    "extraction_method": "ats_api",
    "posted_at": "2026-07-01T00:00:00+00:00",
    "scraped_at": "2026-07-03T10:00:00+00:00",
    "last_seen_at": "2026-07-03T10:00:00+00:00",
    "status": "active",
    "source_channel": "career_page",
}


def _make_admin():
    return _UserRecord(
        user_id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="hash",
        role=_RoleEnum.ADMIN,
    )


def _make_hunter():
    return _UserRecord(
        user_id=uuid.uuid4(),
        email="hunter@example.com",
        password_hash="hash",
        role=_RoleEnum.HUNTER,
    )


def _auth_headers(user=None):
    u = user or _make_admin()
    tok = _encode(
        str(u.user_id), u.role, _TEST_SECRET, _TEST_ALG,
        _dt.now(_tz.utc) + _td(minutes=15),
    )
    return {"Authorization": f"Bearer {tok}"}


def _patch_auth():
    return (
        patch("orchestration.auth.dependencies._get_jwt_config",
              return_value=(_TEST_SECRET, _TEST_ALG)),
        patch("orchestration.auth.dependencies.AuthRepository"),
        patch("orchestration.auth.dependencies.get_session_factory"),
    )


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── GET /api/career-jobs/latest ──────────────────────────────────────────────

class TestLatestCareerJobs:
    def test_returns_job_list(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_jobs = AsyncMock(return_value=([_SAMPLE_JOB], 1))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.career_jobs.CareerJobsService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/career-jobs/latest",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["jobs"][0]["job_title"] == "Python Engineer"
        assert data["jobs"][0]["extraction_method"] == "ats_api"

    def test_hunter_can_access(self, client):
        mock_service = MagicMock()
        mock_service.get_latest_jobs = AsyncMock(return_value=([], 0))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.career_jobs.CareerJobsService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/career-jobs/latest",
                    headers=_auth_headers(_make_hunter()),
                )
        assert resp.status_code == 200

    def test_rejects_invalid_company_uuid_filter(self, client):
        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            resp = client.get(
                "/api/career-jobs/latest?company_id=bad-uuid",
                headers=_auth_headers(),
            )
        assert resp.status_code == 422

    def test_requires_auth(self, client):
        resp = client.get("/api/career-jobs/latest")
        assert resp.status_code == 401


# ── GET /api/career-jobs/counts ──────────────────────────────────────────────

class TestCareerJobCounts:
    def test_returns_counts(self, client):
        mock_service = MagicMock()
        mock_service.get_counts = AsyncMock(return_value={
            "total_jobs": 520,
            "by_status": {"active": 450, "closed": 60, "raw": 10},
            "by_extraction_method": {
                "ats_api": 200, "json_ld": 150,
                "html_parse": 100, "sitemap": 70,
            },
            "active_companies_count": 180,
            "jobs_with_apply_contact": 490,
        })

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.career_jobs.CareerJobsService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/career-jobs/counts",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_jobs"] == 520
        assert data["active_companies_count"] == 180
        assert data["jobs_with_apply_contact"] == 490

    def test_requires_auth(self, client):
        resp = client.get("/api/career-jobs/counts")
        assert resp.status_code == 401
