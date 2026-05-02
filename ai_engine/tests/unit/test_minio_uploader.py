"""Unit tests for MinIO uploader."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from ai_engine.features.output.storage.minio_uploader import MinIOUploader, MinIOUploadError


@pytest.fixture
def uploader():
    """MinIO uploader with mocked S3 client and bucket pre-marked ready."""
    u = MinIOUploader(
        endpoint="localhost:9000",
        access_key="test_key",
        secret_key="test_secret",
        bucket_name="test-bucket",
    )
    u.s3_client = MagicMock()
    u._bucket_ready = True
    return u


@pytest.mark.asyncio
async def test_upload_file_success(uploader, tmp_path):
    test_file = tmp_path / "resume.pdf"
    test_file.write_text("mock pdf content")

    s3_key = await uploader.upload_file(
        test_file, user_id="user-123", job_id="job-456", file_type="resume_pdf"
    )

    assert s3_key.startswith("resumes/user-123/job-456/")
    assert s3_key.endswith("_resume_pdf.pdf")
    uploader.s3_client.upload_file.assert_called_once()


@pytest.mark.asyncio
async def test_upload_file_not_found(uploader):
    with pytest.raises(MinIOUploadError, match="File not found"):
        await uploader.upload_file(
            Path("/nonexistent/file.pdf"),
            user_id="user-123",
            job_id="job-456",
            file_type="resume_pdf",
        )


@pytest.mark.asyncio
async def test_get_signed_url(uploader):
    uploader.s3_client.generate_presigned_url = MagicMock(
        return_value="http://localhost:9000/test-bucket/resumes/user-123/file.pdf?sig=abc"
    )

    url = await uploader.get_signed_url("resumes/user-123/job-456/file.pdf")

    assert "localhost:9000" in url
    uploader.s3_client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_verify_upload_exists(uploader):
    uploader.s3_client.head_object = MagicMock()

    exists = await uploader.verify_upload("resumes/user-123/job-456/file.pdf")

    assert exists is True


@pytest.mark.asyncio
async def test_verify_upload_not_found(uploader):
    error = ClientError({"Error": {"Code": "404"}}, "HeadObject")
    uploader.s3_client.head_object = MagicMock(side_effect=error)

    exists = await uploader.verify_upload("resumes/nonexistent.pdf")

    assert exists is False
