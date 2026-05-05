"""Test fixtures and app client setup."""

import sys
import os
import uuid
import asyncio

import pytest
from fastapi.testclient import TestClient

# Ensure shared package is importable
_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_shared_path = os.path.normpath(os.path.join(_base, "..", "..", "..", "..", "package", "JobHunter-DPL", "JobHunter-DPL"))
if os.path.isdir(_shared_path) and _shared_path not in sys.path:
    sys.path.insert(0, _shared_path)

# Add service root to path
if _base not in sys.path:
    sys.path.insert(0, _base)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client(tmp_path):
    """TestClient with temp registries and auth header."""
    os.environ["REGISTRY_JOBS_PATH"] = str(tmp_path / "jobs.json")
    os.environ["REGISTRY_VARIANTS_PATH"] = str(tmp_path / "variants.json")
    os.environ["REGISTRY_APPLICATIONS_PATH"] = str(tmp_path / "applications.json")
    os.environ["API_KEY_TOKEN"] = "test-secret"

    # Clear lru_cache so settings reload from env
    from config import get_settings
    get_settings.cache_clear()

    # Reset dependency singletons
    import dependencies
    dependencies._job_registry = None
    dependencies._variant_registry = None
    dependencies._application_log = None
    dependencies._minio_uploader = None

    from app import create_app
    test_app = create_app()

    with TestClient(test_app, headers={"Authorization": "Bearer test-secret"}) as c:
        yield c

    get_settings.cache_clear()


@pytest.fixture
def sample_job_id():
    return str(uuid.uuid4())


@pytest.fixture
def sample_variant_payload():
    return {
        "user_id": "user-001",
        "job_id": str(uuid.uuid4()),
        "master_resume_id": str(uuid.uuid4()),
        "pdf_key": "resumes/user-001/job-x/resume.pdf",
        "docx_key": "resumes/user-001/job-x/resume.docx",
        "cover_letter_key": "",
        "curated_json": {"name": "Test User"},
        "gaps_identified": [],
        "approval_status": "pending",
    }


@pytest.fixture
def sample_application_payload():
    return {
        "user_id": "user-001",
        "job_id": str(uuid.uuid4()),
        "resume_variant_id": str(uuid.uuid4()),
        "cover_letter_id": None,
        "email_subject": "Application for Python Developer",
    }
