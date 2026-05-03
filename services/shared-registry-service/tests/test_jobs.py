"""Tests for /api/jobs endpoints."""

import uuid


def test_get_job_not_found(client):
    response = client.get(f"/api/jobs/{uuid.uuid4()}")
    assert response.status_code == 404


def test_get_job_invalid_id(client):
    response = client.get("/api/jobs/not-a-uuid")
    assert response.status_code == 400


def test_get_jobs_by_source_empty(client):
    response = client.get("/api/jobs/by-source/naukri")
    assert response.status_code == 200
    assert response.json() == []


def test_get_jobs_by_status_empty(client):
    response = client.get("/api/jobs/status/raw")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_with_email_empty(client):
    response = client.get("/api/jobs/all-with-email")
    assert response.status_code == 200
    assert response.json() == []


def test_auth_required(client):
    from fastapi.testclient import TestClient
    from app import create_app
    unauth_client = TestClient(create_app())
    response = unauth_client.get(f"/api/jobs/{uuid.uuid4()}")
    assert response.status_code == 401


def test_health_no_auth(client):
    from fastapi.testclient import TestClient
    from app import create_app
    unauth_client = TestClient(create_app())
    response = unauth_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
