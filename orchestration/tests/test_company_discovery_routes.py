"""Tests for /api/company-discovery/* routes using FastAPI TestClient."""

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

_FAKE_RUN_ID = str(uuid.uuid4())
_FAKE_COMPANY_ID = str(uuid.uuid4())


def _make_admin():
    return _UserRecord(
        user_id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="hash",
        role=_RoleEnum.ADMIN,
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


# ── POST /api/company-discovery/start ────────────────────────────────────────

class TestStartDiscovery:
    def test_returns_201_with_run_id(self, client):
        mock_service = MagicMock()
        mock_service.trigger_discovery = AsyncMock(return_value=uuid.UUID(_FAKE_RUN_ID))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.post(
                    "/api/company-discovery/start",
                    json={"role": "python developer", "location": "Bangalore"},
                    headers=_auth_headers(),
                )

        assert resp.status_code == 201
        data = resp.json()
        assert data["run_id"] == _FAKE_RUN_ID
        assert data["status"] == "queued"
        assert "started_at" in data

    def test_requires_auth(self, client):
        resp = client.post(
            "/api/company-discovery/start",
            json={"role": "developer", "location": "Mumbai"},
        )
        assert resp.status_code == 401

    def test_validates_required_fields(self, client):
        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            resp = client.post(
                "/api/company-discovery/start",
                json={"role": "developer"},  # missing location
                headers=_auth_headers(),
            )
        assert resp.status_code == 422


# ── POST /api/company-discovery/bootstrap ────────────────────────────────────

class TestRunBootstrap:
    def test_returns_201_with_run_id(self, client):
        mock_service = MagicMock()
        mock_service.trigger_bootstrap = AsyncMock(return_value=uuid.UUID(_FAKE_RUN_ID))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.post(
                    "/api/company-discovery/bootstrap",
                    json={"sources": ["all"]},
                    headers=_auth_headers(),
                )

        assert resp.status_code == 201
        assert resp.json()["status"] == "queued"

    def test_default_sources_is_all(self, client):
        mock_service = MagicMock()
        mock_service.trigger_bootstrap = AsyncMock(return_value=uuid.UUID(_FAKE_RUN_ID))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.post(
                    "/api/company-discovery/bootstrap",
                    json={},
                    headers=_auth_headers(),
                )

        assert resp.status_code == 201
        mock_service.trigger_bootstrap.assert_called_once()


# ── GET /api/company-discovery/status/{run_id} ───────────────────────────────

class TestDiscoveryStatus:
    def test_returns_status_for_known_run(self, client):
        mock_service = MagicMock()
        mock_service.get_run_status = AsyncMock(return_value={
            "run_id": _FAKE_RUN_ID,
            "source": "company_discovery_bootstrap",
            "started_at": "2026-07-03T10:00:00+00:00",
            "completed_at": None,
            "status": "running",
            "companies_found": 42,
            "errors": 0,
            "error_detail": None,
        })

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.get(
                    f"/api/company-discovery/status/{_FAKE_RUN_ID}",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["companies_found"] == 42
        assert data["status"] == "running"

    def test_returns_404_for_unknown_run(self, client):
        mock_service = MagicMock()
        mock_service.get_run_status = AsyncMock(return_value=None)

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.get(
                    f"/api/company-discovery/status/{uuid.uuid4()}",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 404


# ── GET /api/company-discovery/companies ────────────────────────────────────

class TestListCompanies:
    def test_returns_paginated_company_list(self, client):
        mock_service = MagicMock()
        mock_service.get_companies = AsyncMock(return_value=(
            [{
                "company_id": _FAKE_COMPANY_ID,
                "company_name": "Acme Corp",
                "apex_domain": "acme.com",
                "career_page_url": "https://acme.com/careers",
                "career_emails": ["hr@acme.com"],
                "email_trust": "unverified",
                "ats_platform": "greenhouse",
                "industry": "Technology",
                "hq_location": "Bangalore",
                "source": "vc_portfolio",
                "crawl_status": "enriched",
                "discovery_date": "2026-07-03T10:00:00+00:00",
                "last_enriched_at": "2026-07-03T11:00:00+00:00",
            }],
            1,
        ))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/company-discovery/companies",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["companies"][0]["apex_domain"] == "acme.com"

    def test_passes_filters_to_service(self, client):
        mock_service = MagicMock()
        mock_service.get_companies = AsyncMock(return_value=([], 0))

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/company-discovery/companies?crawl_status=enriched&ats_platform=greenhouse",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        mock_service.get_companies.assert_called_once_with(
            crawl_status="enriched", ats_platform="greenhouse", limit=50, offset=0
        )


# ── GET /api/company-discovery/stats ─────────────────────────────────────────

class TestCompanyStats:
    def test_returns_stats(self, client):
        mock_service = MagicMock()
        mock_service.get_stats = AsyncMock(return_value={
            "total_companies": 350,
            "by_crawl_status": {"enriched": 300, "pending": 50},
            "by_ats_platform": {"greenhouse": 120, "custom": 180},
            "with_career_page_url": 310,
            "with_career_email": 200,
            "low_trust_email_count": 15,
        })

        p1, p2, p3 = _patch_auth()
        with p1, p2, p3:
            with patch(
                "orchestration.api.routes.company_discovery.CompanyDiscoveryService",
                return_value=mock_service,
            ):
                resp = client.get(
                    "/api/company-discovery/stats",
                    headers=_auth_headers(),
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_companies"] == 350
        assert data["with_career_page_url"] == 310
