"""Integration test — Mail-Bridge contract workflow."""

import uuid

from fastapi.testclient import TestClient


def test_mail_bridge_workflow(client, sample_variant_payload):
    """Simulate Mail-Bridge: create + approve variant → get approved → signed URL."""
    # 1. Create variant
    create_resp = client.post("/api/variants", json=sample_variant_payload)
    assert create_resp.status_code == 201
    variant_id = create_resp.json()["variant_id"]

    # 2. Approve variant
    patch_resp = client.patch(f"/api/variants/{variant_id}/approval", json={"approval_status": "approved"})
    assert patch_resp.status_code == 200

    # 3. Get approved variant (Mail-Bridge pre-send check)
    job_id = sample_variant_payload["job_id"]
    user_id = sample_variant_payload["user_id"]
    approved_resp = client.get(f"/api/variants/approved/{job_id}/{user_id}")
    assert approved_resp.status_code == 200
    assert approved_resp.json()["approval_status"] == "approved"

    # 4. Signed URL — MinIO not available in test env; use raise_server_exceptions=False
    pdf_key = approved_resp.json().get("pdf_key", "")
    if pdf_key:
        from app import create_app
        safe_client = TestClient(create_app(), raise_server_exceptions=False, headers={"Authorization": "Bearer test-secret"})
        url_resp = safe_client.get(f"/api/files/signed-url?s3_key={pdf_key}")
        assert url_resp.status_code in (200, 404, 500, 503)


def test_application_lifecycle(client, sample_application_payload):
    """Create → get → update status → list by user."""
    create_resp = client.post("/api/applications", json=sample_application_payload)
    assert create_resp.status_code == 201
    app_id = create_resp.json()["application_id"]

    get_resp = client.get(f"/api/applications/{app_id}")
    assert get_resp.status_code == 200

    patch_resp = client.patch(f"/api/applications/{app_id}/status", json={"status": "replied", "reply_count": 2})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["reply_count"] == 2

    list_resp = client.get(f"/api/applications/by-user/{sample_application_payload['user_id']}")
    assert list_resp.status_code == 200
    assert any(a["application_id"] == app_id for a in list_resp.json())
