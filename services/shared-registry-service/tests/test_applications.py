"""Tests for /api/applications endpoints."""

import uuid


def test_get_application_not_found(client):
    response = client.get(f"/api/applications/{uuid.uuid4()}")
    assert response.status_code == 404


def test_get_application_invalid_id(client):
    response = client.get("/api/applications/bad-id")
    assert response.status_code == 400


def test_create_application(client, sample_application_payload):
    response = client.post("/api/applications", json=sample_application_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == sample_application_payload["user_id"]
    assert data["status"] == "sent"
    assert "application_id" in data


def test_create_application_duplicate(client, sample_application_payload):
    client.post("/api/applications", json=sample_application_payload)
    response = client.post("/api/applications", json=sample_application_payload)
    assert response.status_code == 409


def test_get_application_after_create(client, sample_application_payload):
    create_resp = client.post("/api/applications", json=sample_application_payload)
    app_id = create_resp.json()["application_id"]
    get_resp = client.get(f"/api/applications/{app_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["application_id"] == app_id


def test_update_application_status(client, sample_application_payload):
    create_resp = client.post("/api/applications", json=sample_application_payload)
    app_id = create_resp.json()["application_id"]
    patch_resp = client.patch(f"/api/applications/{app_id}/status", json={"status": "replied", "reply_count": 1})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "replied"
    assert patch_resp.json()["reply_count"] == 1


def test_get_applications_by_user(client, sample_application_payload):
    client.post("/api/applications", json=sample_application_payload)
    resp = client.get(f"/api/applications/by-user/{sample_application_payload['user_id']}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_sent_today(client, sample_application_payload):
    client.post("/api/applications", json=sample_application_payload)
    resp = client.get(f"/api/applications/sent-today/{sample_application_payload['user_id']}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_applications_by_job(client, sample_application_payload):
    client.post("/api/applications", json=sample_application_payload)
    job_id = sample_application_payload["job_id"]
    resp = client.get(f"/api/applications/by-job/{job_id}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
