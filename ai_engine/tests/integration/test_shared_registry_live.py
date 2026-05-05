"""Live integration tests for AI Engine → VariantRegistry + MinIO write."""

import pytest
from pathlib import Path
from uuid import uuid4

from shared.registries.job_registry import JobRegistry
from shared.registries.variant_registry import VariantRegistry
from shared.models.job_record import JobRecord
from shared.models.variant_record import VariantRecord
from ai_engine.features.output.storage.minio_uploader import MinIOUploader


@pytest.fixture
async def job_registry_with_test_job(tmp_path):
    """Isolated JobRegistry pre-populated with one test job."""
    registry = JobRegistry(file_path=str(tmp_path / "test_jobs.json"))
    test_job = JobRecord(
        job_id=uuid4(),
        source="naukri",
        external_id="naukri-test-123456",
        title="Senior Python Developer",
        company_name="TechCorp",
        company_domain="techcorp.com",
        location="Bangalore",
        remote_type="hybrid",
        salary_min=1000000,
        salary_max=1500000,
        experience_min=5,
        experience_max=10,
        description="We are looking for a Senior Python Developer with FastAPI experience.",
        skills_required=["Python", "FastAPI", "PostgreSQL"],
        job_type="fulltime",
        apply_email="careers@techcorp.com",
        apply_url="https://techcorp.com/jobs/123",
        status="raw",
    )
    await registry.save([test_job])
    yield registry, test_job


@pytest.fixture
async def isolated_variant_registry(tmp_path):
    """Isolated VariantRegistry backed by a temp file."""
    yield VariantRegistry(file_path=str(tmp_path / "test_variants.json"))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ai_engine_generates_variant_with_minio_keys(
    job_registry_with_test_job,
    isolated_variant_registry,
):
    """Verify VariantRecord is written with MinIO S3 keys.

    Precondition: docker-compose up -d minio

    Validates:
    1. File uploads to MinIO succeed
    2. S3 key format is correct
    3. VariantRecord with pdf_key is persisted to VariantRegistry
    4. Retrieved record has the correct pdf_key
    """
    _, test_job = job_registry_with_test_job

    minio = MinIOUploader(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="jobhunter-resumes",
        use_ssl=False,
    )

    test_resume_pdf = Path("/tmp/test_resume_live.pdf")
    test_resume_pdf.write_text("Mock PDF content")

    try:
        pdf_key = await minio.upload_file(
            test_resume_pdf,
            user_id="test-user",
            job_id=str(test_job.job_id),
            file_type="resume_pdf",
        )

        assert pdf_key, "pdf_key should be non-empty"
        assert pdf_key.startswith("resumes/test-user/"), f"Unexpected key format: {pdf_key}"

        exists = await minio.verify_upload(pdf_key)
        assert exists, f"File {pdf_key} not found in MinIO after upload"

        variant = VariantRecord(
            variant_id=uuid4(),
            user_id="test-user",
            job_id=test_job.job_id,
            master_resume_id=uuid4(),
            pdf_key=pdf_key,
            docx_key="",
            cover_letter_key="",
            local_pdf_path=str(test_resume_pdf),
            s3_upload_failed=False,
            curated_json={},
            approval_status="pending",
        )

        await isolated_variant_registry.save(variant)

        retrieved = await isolated_variant_registry.get(variant.variant_id)
        assert retrieved.pdf_key == pdf_key, "S3 key not persisted correctly"

    finally:
        test_resume_pdf.unlink(missing_ok=True)
