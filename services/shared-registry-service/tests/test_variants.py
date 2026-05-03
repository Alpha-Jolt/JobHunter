"""Tests for /api/variants endpoints."""

import uuid


def test_get_variant_not_found(client):
    response = client.get(f"/api/variants/{uuid.uuid4()}")
    assert response.status_code == 404


def test_get_variant_invalid_id(client):
    response = client.get("/api/variants/bad-id")
    assert response.status_code == 400


def test_create_variant(client, sample_variant_payload):
    response = client.post("/api/variants", json=sample_variant_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == sample_variant_payload["user_id"]
    assert data["approval_status"] == "pending"
    assert "variant_id" in data


def test_create_variant_duplicate(client, sample_variant_payload):
    client.post("/api/variants", json=sample_variant_payload)
    response = client.post("/api/variants", json=sample_variant_payload)
    assert response.status_code == 409


def test_get_variant_after_create(client, sample_variant_payload):
    create_resp = client.post("/api/variants", json=sample_variant_payload)
    variant_id = create_resp.json()["variant_id"]
    get_resp = client.get(f"/api/variants/{variant_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["variant_id"] == variant_id


def test_update_approval(client, sample_variant_payload):
    create_resp = client.post("/api/variants", json=sample_variant_payload)
    variant_id = create_resp.json()["variant_id"]
    patch_resp = client.patch(f"/api/variants/{variant_id}/approval", json={"approval_status": "approved"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["approval_status"] == "approved"


def test_update_approval_invalid_status(client, sample_variant_payload):
    create_resp = client.post("/api/variants", json=sample_variant_payload)
    variant_id = create_resp.json()["variant_id"]
    response = client.patch(f"/api/variants/{variant_id}/approval", json={"approval_status": "invalid"})
    assert response.status_code == 400


def test_get_approved_variant(client, sample_variant_payload):
    create_resp = client.post("/api/variants", json=sample_variant_payload)
    variant_id = create_resp.json()["variant_id"]
    client.patch(f"/api/variants/{variant_id}/approval", json={"approval_status": "approved"})

    job_id = sample_variant_payload["job_id"]
    user_id = sample_variant_payload["user_id"]
    resp = client.get(f"/api/variants/approved/{job_id}/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["approval_status"] == "approved"


def test_get_approved_variant_not_found(client):
    resp = client.get(f"/api/variants/approved/{uuid.uuid4()}/user-999")
    assert resp.status_code == 404


def test_get_variants_for_user_empty(client):
    resp = client.get("/api/variants/for-user/unknown-user")
    assert resp.status_code == 200
    assert resp.json() == []
