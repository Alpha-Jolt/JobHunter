"""Integration tests for AI Engine service layer and API routes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON

import orchestration.db.models as _prod_models
from orchestration.repositories.postgres_variant_repository import PostgresVariantRepository
from orchestration.services.ai_service import AIService, AIServiceError
from orchestration.services.approval_service import (
    ApprovalService,
    TokenAlreadyUsedError,
    TokenExpiredError,
    TokenInvalidError,
)
from orchestration.services.storage_service import StorageService
from shared.models.exceptions import RegistryError, VariantNotFoundError
from shared.models.variant_record import VariantRecord

# ── SQLite-compatible test models ─────────────────────────────────────────────

_SECRET = "test-secret-key-32-chars-minimum!!"


class TestBase(DeclarativeBase):
    pass


class Job(TestBase):
    __tablename__ = "jobs"
    job_id = Column(String(36), primary_key=True)
    source = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    company_name = Column(String(255), nullable=False)
    company_domain = Column(String(255))
    location = Column(String(255))
    remote_type = Column(String(20))
    salary_min = Column(String(20))
    salary_max = Column(String(20))
    experience_min = Column(Integer)
    experience_max = Column(Integer)
    description = Column(Text, nullable=False)
    skills_required = Column(JSON, nullable=False, default=list)
    job_type = Column(String(20), nullable=False, default="fulltime")
    apply_email = Column(String(255))
    email_trust = Column(String(20), nullable=False, default="unknown")
    apply_url = Column(Text)
    posted_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True))
    last_seen_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="raw")
    created_at = Column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="jobs_source_external_id_unique"),
    )


class MasterResume(TestBase):
    __tablename__ = "master_resumes"
    resume_id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class ResumeVariant(TestBase):
    __tablename__ = "resume_variants"
    variant_id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.job_id"), nullable=False)
    master_resume_id = Column(String(36), ForeignKey("master_resumes.resume_id"), nullable=False)
    pdf_key = Column(Text, nullable=False, default="")
    docx_key = Column(Text, nullable=False, default="")
    cover_letter_key = Column(Text, nullable=False, default="")
    local_pdf_path = Column(Text, nullable=False, default="")
    s3_upload_failed = Column(Boolean, nullable=False, default=False)
    curated_json = Column(JSON, nullable=False, default=dict)
    gaps_identified = Column(JSON, nullable=False, default=list)
    approval_status = Column(String(20), nullable=False, default="pending")
    approval_token = Column(String(256))
    approved_at = Column(DateTime(timezone=True))
    user_feedback = Column(Text)
    prompt_version = Column(String(50), nullable=False, default="")
    created_at = Column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="resume_variants_user_job_unique"),
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """In-memory SQLite session with patched prod models."""
    _prod_models.Job = Job
    _prod_models.MasterResume = MasterResume
    _prod_models.ResumeVariant = ResumeVariant

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest.fixture
def approval_service(session):
    repo = PostgresVariantRepository(session)
    return ApprovalService(variant_registry=repo, secret_key=_SECRET)


@pytest.fixture
def test_user_id() -> str:
    return "test-user-001"


@pytest.fixture
def test_resume_path(tmp_path) -> Path:
    p = tmp_path / "resume.pdf"
    p.write_bytes(b"%PDF-1.4 fake resume content")
    return p


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _insert_job_row(session, job_id: str = None) -> str:
    jid = job_id or str(uuid.uuid4())
    row = Job(
        job_id=jid,
        source="naukri",
        external_id=f"ext-{jid[:8]}",
        title="Python Developer",
        company_name="Acme Corp",
        description="Build cool stuff with Python and FastAPI",
        skills_required=["Python", "FastAPI"],
        job_type="fulltime",
        email_trust="verified",
        status="raw",
        apply_email="hr@acme.com",
        last_seen_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    session.add(row)
    await session.flush()
    return jid


async def _insert_master_resume(session, user_id: str) -> str:
    rid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    row = MasterResume(
        resume_id=rid,
        user_id=user_id,
        file_name="resume.pdf",
        file_path="/tmp/resume.pdf",
        parsed_json={},
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    return rid


async def _create_pending_variant(
    session, user_id: str, job_id: str, approval_svc: ApprovalService
) -> VariantRecord:
    """Insert a pending variant directly into the DB and return VariantRecord."""
    resume_id = await _insert_master_resume(session, user_id)
    vid = uuid.uuid4()
    token = approval_svc.generate_approval_token(str(vid), "test@example.com")
    now = datetime.now(timezone.utc)
    row = ResumeVariant(
        variant_id=str(vid),
        user_id=user_id,
        job_id=job_id,
        master_resume_id=resume_id,
        pdf_key="test/resume.pdf",
        docx_key="test/resume.docx",
        cover_letter_key="",
        local_pdf_path="",
        s3_upload_failed=False,
        curated_json={
            "personal": {"name": "Test User", "email": "test@example.com"},
            "summary": "Experienced developer",
            "experience": [],
            "skills": ["Python", "FastAPI"],
            "match_score": 85,
        },
        gaps_identified=["Docker", "Kubernetes"],
        approval_status="pending",
        approval_token=token,
        prompt_version="v1",
        created_at=now,
    )
    session.add(row)
    await session.flush()

    return VariantRecord(
        variant_id=vid,
        user_id=user_id,
        job_id=uuid.UUID(job_id),
        master_resume_id=uuid.UUID(resume_id),
        pdf_key="test/resume.pdf",
        docx_key="test/resume.docx",
        approval_status="pending",
        approval_token=token,
        curated_json={
            "personal": {"name": "Test User", "email": "test@example.com"},
            "summary": "Experienced developer",
            "experience": [],
            "skills": ["Python", "FastAPI"],
            "match_score": 85,
        },
        gaps_identified=["Docker", "Kubernetes"],
        created_at=now,
    )


def _make_expired_token(variant_id: str) -> str:
    """Create a token with a timestamp 25 hours in the past."""
    old_ts = int(time.time()) - (25 * 3600)
    message = f"{variant_id}:{old_ts}".encode()
    sig = hmac.new(_SECRET.encode(), message, hashlib.sha256).digest()
    b64_sig = base64.urlsafe_b64encode(sig).decode()
    return f"{variant_id}:{old_ts}:{b64_sig}"


# ── TASK 2.4: 10 Integration Tests ───────────────────────────────────────────

def _make_job_record(job_id: str) -> "JobRecord":
    """Create a minimal valid DPL JobRecord for testing."""
    from shared.models.job_record import JobRecord
    return JobRecord(
        job_id=uuid.UUID(job_id),
        source="naukri",
        external_id=f"ext-{job_id[:8]}",
        title="Python Developer",
        company_name="Acme Corp",
        company_domain="acme.com",
        location="Bangalore",
        remote_type="hybrid",
        salary_min=None,
        salary_max=None,
        experience_min=None,
        experience_max=None,
        description="Build cool stuff with Python and FastAPI",
        skills_required=["Python"],
        job_type="fulltime",
        apply_email="hr@acme.com",
        email_trust="verified",
        status="raw",
    )


@pytest.mark.asyncio
async def test_generate_variant_creates_pending_record(session, test_user_id, test_resume_path):
    """Variant is stored in DB with status=pending after generate_variant()."""
    job_id = await _insert_job_row(session)
    resume_id = str(uuid.uuid4())

    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    # Mock master_resume_registry
    mock_mr_registry = MagicMock()
    mock_mr_registry.get_or_create = AsyncMock(
        return_value=(uuid.UUID(resume_id), {}, "v1")
    )

    # Mock storage
    storage = StorageService(output_dir=str(test_resume_path.parent))
    storage.upload_file = AsyncMock(return_value="test/key")

    # Mock AI pipeline internals
    mock_pipeline = MagicMock()
    mock_executor = MagicMock()
    mock_pipeline._executor = mock_executor

    from ai_engine.features.resume.models.resume_schema import (
        PersonalInfo,
        ResumeData,
    )
    from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
    from ai_engine.features.matching.models.comparison_result import ComparisonResult
    from ai_engine.features.analysis.models.job_analysis import JobAnalysis

    mock_resume = ResumeData(
        personal=PersonalInfo(name="Test User", email="test@example.com"),
        summary="Developer",
        skills=["Python"],
    )
    mock_analysis = MagicMock(spec=JobAnalysis)
    mock_comparison = ComparisonResult(match_score=85, matched_skills=["Python"], gap_skills=["Docker"])
    mock_variant = OptimisedVariant(
        rewritten_summary="Experienced developer",
        prioritized_skills=["Python"],
        gaps=["Docker"],
        prompt_version_used="v1",
        job_id=job_id,
    )

    mock_executor._resume_parser = MagicMock()
    mock_executor._resume_parser.parse = AsyncMock(return_value=mock_resume)
    mock_executor._job_analyser = MagicMock()
    mock_executor._job_analyser.analyse = AsyncMock(return_value=mock_analysis)
    mock_executor._comparator = MagicMock()
    mock_executor._comparator.compare = AsyncMock(return_value=mock_comparison)
    mock_executor._optimiser = MagicMock()
    mock_executor._optimiser.optimise = AsyncMock(return_value=mock_variant)

    job_record = _make_job_record(job_id)

    ai_service = AIService(
        variant_registry=variant_repo,
        job_registry=MagicMock(),
        master_resume_registry=mock_mr_registry,
        approval_service=approval_svc,
        storage_service=storage,
        ai_pipeline=mock_pipeline,
    )

    variant = await ai_service.generate_variant(
        user_id=test_user_id,
        job_id=job_id,
        master_resume_path=str(test_resume_path),
        job_record=job_record,
    )

    assert variant.approval_status == "pending"
    assert variant.variant_id is not None
    assert variant.approval_token is not None

    # Verify in DB
    stored = await variant_repo.get(variant.variant_id)
    assert stored.approval_status == "pending"
    assert stored.user_id == test_user_id


@pytest.mark.asyncio
async def test_generate_variant_produces_valid_approval_token(
    session, test_user_id, test_resume_path
):
    """Approval token generated during variant creation is valid and parseable."""
    job_id = await _insert_job_row(session)
    resume_id = str(uuid.uuid4())

    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    mock_mr_registry = MagicMock()
    mock_mr_registry.get_or_create = AsyncMock(return_value=(uuid.UUID(resume_id), {}, "v1"))

    storage = StorageService(output_dir=str(test_resume_path.parent))
    storage.upload_file = AsyncMock(return_value="test/key")

    mock_pipeline = MagicMock()
    mock_executor = MagicMock()
    mock_pipeline._executor = mock_executor

    from ai_engine.features.resume.models.resume_schema import PersonalInfo, ResumeData
    from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
    from ai_engine.features.matching.models.comparison_result import ComparisonResult

    mock_executor._resume_parser = MagicMock()
    mock_executor._resume_parser.parse = AsyncMock(
        return_value=ResumeData(personal=PersonalInfo(name="Test"), skills=["Python"])
    )
    mock_executor._job_analyser = MagicMock()
    mock_executor._job_analyser.analyse = AsyncMock(return_value=MagicMock())
    mock_executor._comparator = MagicMock()
    mock_executor._comparator.compare = AsyncMock(
        return_value=ComparisonResult(match_score=80, matched_skills=["Python"], gap_skills=[])
    )
    mock_executor._optimiser = MagicMock()
    mock_executor._optimiser.optimise = AsyncMock(
        return_value=OptimisedVariant(
            prioritized_skills=["Python"], gaps=[], prompt_version_used="v1", job_id=job_id
        )
    )

    job_record = _make_job_record(job_id)

    ai_service = AIService(
        variant_registry=variant_repo,
        job_registry=MagicMock(),
        master_resume_registry=mock_mr_registry,
        approval_service=approval_svc,
        storage_service=storage,
        ai_pipeline=mock_pipeline,
    )

    variant = await ai_service.generate_variant(
        user_id=test_user_id,
        job_id=job_id,
        master_resume_path=str(test_resume_path),
        job_record=job_record,
    )

    token = variant.approval_token
    assert token is not None
    parts = token.split(":")
    assert len(parts) == 3, "Token must have 3 colon-separated parts"

    # Token should be valid (not expired)
    recovered_id = approval_svc.validate_approval_token(token)
    assert recovered_id == str(variant.variant_id)


@pytest.mark.asyncio
async def test_preview_variant_returns_curated_json(session, test_user_id):
    """get_variant_details returns curated_resume with expected structure."""
    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)

    ai_service = AIService(
        variant_registry=variant_repo,
        job_registry=MagicMock(),
        master_resume_registry=MagicMock(),
        approval_service=approval_svc,
        storage_service=MagicMock(),
        ai_pipeline=MagicMock(),
    )

    details = await ai_service.get_variant_details(str(variant.variant_id))

    assert "curated_resume" in details
    assert "gaps" in details
    assert isinstance(details["gaps"], list)
    assert "personal" in details["curated_resume"]
    assert "skills" in details["curated_resume"]
    assert details["approval_status"] == "pending"


@pytest.mark.asyncio
async def test_approve_with_valid_token_changes_status(session, test_user_id):
    """Approving with a valid token sets approval_status to 'approved'."""
    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)
    token = variant.approval_token

    recovered_id = approval_svc.validate_approval_token(token)
    assert recovered_id == str(variant.variant_id)

    updated = await approval_svc.mark_approved(str(variant.variant_id))
    assert updated.approval_status == "approved"
    assert updated.approved_at is not None

    # Verify in DB
    stored = await variant_repo.get(variant.variant_id)
    assert stored.approval_status == "approved"
    assert stored.approved_at is not None


@pytest.mark.asyncio
async def test_approve_with_invalid_token_returns_error(session, test_user_id):
    """Invalid token raises TokenInvalidError; variant stays pending."""
    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)

    with pytest.raises(TokenInvalidError):
        approval_svc.validate_approval_token("garbage_token_here")

    # Variant still pending
    stored = await variant_repo.get(variant.variant_id)
    assert stored.approval_status == "pending"


@pytest.mark.asyncio
async def test_approve_with_expired_token_returns_error(session, test_user_id):
    """Expired token raises TokenExpiredError; variant stays pending."""
    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)
    expired_token = _make_expired_token(str(variant.variant_id))

    with pytest.raises(TokenExpiredError):
        approval_svc.validate_approval_token(expired_token)

    stored = await variant_repo.get(variant.variant_id)
    assert stored.approval_status == "pending"


@pytest.mark.asyncio
async def test_cannot_approve_already_approved_variant(session, test_user_id):
    """Approving an already-approved variant raises TokenAlreadyUsedError."""
    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)

    # First approval
    await approval_svc.mark_approved(str(variant.variant_id))

    # Second approval attempt
    with pytest.raises(TokenAlreadyUsedError):
        await approval_svc.mark_approved(str(variant.variant_id))


@pytest.mark.asyncio
async def test_reject_variant_stores_feedback(session, test_user_id):
    """Rejecting a variant sets status to 'rejected' and stores feedback."""
    from sqlalchemy import select, update
    import orchestration.db.models as _m

    job_id = await _insert_job_row(session)
    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    variant = await _create_pending_variant(session, test_user_id, job_id, approval_svc)
    feedback_text = "Please emphasize ML projects more"

    # Reject and store feedback
    await variant_repo.update_approval_status(variant.variant_id, "rejected")
    await session.execute(
        update(_m.ResumeVariant)
        .where(_m.ResumeVariant.variant_id == str(variant.variant_id))
        .values(user_feedback=feedback_text)
    )
    await session.flush()

    # Verify
    result = await session.execute(
        select(_m.ResumeVariant).where(
            _m.ResumeVariant.variant_id == str(variant.variant_id)
        )
    )
    row = result.scalar_one()
    assert row.approval_status == "rejected"
    assert row.user_feedback == feedback_text


@pytest.mark.asyncio
async def test_pending_variants_excludes_approved(session, test_user_id):
    """get_pending_for_user returns only pending variants, not approved/rejected."""
    job_id_1 = await _insert_job_row(session)
    job_id_2 = await _insert_job_row(session)
    job_id_3 = await _insert_job_row(session)

    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    v1 = await _create_pending_variant(session, test_user_id, job_id_1, approval_svc)
    v2 = await _create_pending_variant(session, test_user_id, job_id_2, approval_svc)
    v3 = await _create_pending_variant(session, test_user_id, job_id_3, approval_svc)

    # Approve v1, reject v2, leave v3 pending
    await approval_svc.mark_approved(str(v1.variant_id))
    await variant_repo.update_approval_status(v2.variant_id, "rejected")

    pending = await variant_repo.get_pending_for_user(test_user_id)
    assert len(pending) == 1
    assert str(pending[0].variant_id) == str(v3.variant_id)


@pytest.mark.asyncio
async def test_generate_variant_rejects_duplicate(session, test_user_id, test_resume_path):
    """Generating a second variant for the same (user_id, job_id) raises AIServiceError."""
    job_id = await _insert_job_row(session)
    resume_id = str(uuid.uuid4())

    variant_repo = PostgresVariantRepository(session)
    approval_svc = ApprovalService(variant_registry=variant_repo, secret_key=_SECRET)

    mock_mr_registry = MagicMock()
    mock_mr_registry.get_or_create = AsyncMock(return_value=(uuid.UUID(resume_id), {}, "v1"))

    storage = StorageService(output_dir=str(test_resume_path.parent))
    storage.upload_file = AsyncMock(return_value="test/key")

    mock_pipeline = MagicMock()
    mock_executor = MagicMock()
    mock_pipeline._executor = mock_executor

    from ai_engine.features.resume.models.resume_schema import PersonalInfo, ResumeData
    from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
    from ai_engine.features.matching.models.comparison_result import ComparisonResult

    mock_executor._resume_parser = MagicMock()
    mock_executor._resume_parser.parse = AsyncMock(
        return_value=ResumeData(personal=PersonalInfo(name="Test"), skills=["Python"])
    )
    mock_executor._job_analyser = MagicMock()
    mock_executor._job_analyser.analyse = AsyncMock(return_value=MagicMock())
    mock_executor._comparator = MagicMock()
    mock_executor._comparator.compare = AsyncMock(
        return_value=ComparisonResult(match_score=80, matched_skills=["Python"], gap_skills=[])
    )
    mock_executor._optimiser = MagicMock()
    mock_executor._optimiser.optimise = AsyncMock(
        return_value=OptimisedVariant(
            prioritized_skills=["Python"], gaps=[], prompt_version_used="v1", job_id=job_id
        )
    )

    job_record = _make_job_record(job_id)

    ai_service = AIService(
        variant_registry=variant_repo,
        job_registry=MagicMock(),
        master_resume_registry=mock_mr_registry,
        approval_service=approval_svc,
        storage_service=storage,
        ai_pipeline=mock_pipeline,
    )

    # First generation — should succeed
    await ai_service.generate_variant(
        user_id=test_user_id,
        job_id=job_id,
        master_resume_path=str(test_resume_path),
        job_record=job_record,
    )

    # Second generation — should raise AIServiceError (duplicate)
    with pytest.raises(AIServiceError):
        await ai_service.generate_variant(
            user_id=test_user_id,
            job_id=job_id,
            master_resume_path=str(test_resume_path),
            job_record=job_record,
        )

    # Only 1 variant in DB
    variants = await variant_repo.get_for_user(test_user_id)
    assert len(variants) == 1
