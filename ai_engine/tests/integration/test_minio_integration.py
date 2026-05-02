"""Integration tests for MinIO file uploads (requires running MinIO service)."""

import pytest
from pathlib import Path

from ai_engine.features.output.storage.minio_uploader import MinIOUploader


@pytest.mark.integration
@pytest.mark.asyncio
async def test_minio_upload_and_verify():
    """Test real MinIO upload. Precondition: docker-compose up -d minio"""
    uploader = MinIOUploader(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="jobhunter-resumes",
        use_ssl=False,
    )

    test_file = Path("/tmp/test_resume.pdf")
    test_file.write_text("Mock PDF content for testing")

    try:
        s3_key = await uploader.upload_file(
            test_file,
            user_id="test-user-123",
            job_id="test-job-456",
            file_type="resume_pdf",
        )

        assert s3_key.startswith("resumes/test-user-123/test-job-456/")

        exists = await uploader.verify_upload(s3_key)
        assert exists, f"File {s3_key} not found in MinIO after upload"

        url = await uploader.get_signed_url(s3_key, expires_in_hours=1)
        assert "localhost:9000" in url

    finally:
        test_file.unlink(missing_ok=True)
