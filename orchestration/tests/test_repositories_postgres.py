"""Tests for PostgreSQL repository implementations using SQLite-compatible schema."""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON

from shared.models.application_record import ApplicationRecord
from shared.models.exceptions import (
    ApplicationNotFoundError, JobNotFoundError, RegistryError, VariantNotFoundError,
)
from shared.models.job_record import JobRecord
from shared.models.variant_record import VariantRecord
from orchestration.repositories.postgres_job_repository import PostgresJobRepository
from orchestration.repositories.postgres_variant_repository import PostgresVariantRepository
from orchestration.repositories.postgres_application_repository import PostgresApplicationRepository


# ── SQLite-compatible test models ─────────────────────────────────────────────

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
    salary_min = Column(Numeric(12, 2))
    salary_max = Column(Numeric(12, 2))
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
    approval_token = Column(String(128))
    approved_at = Column(DateTime(timezone=True))
    user_feedback = Column(Text)
    prompt_version = Column(String(50), nullable=False, default="")
    created_at = Column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="resume_variants_user_job_unique"),
    )


class ApplicationLog(TestBase):
    __tablename__ = "application_log"
    application_id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.job_id"), nullable=False)
    resume_variant_id = Column(String(36), ForeignKey("resume_variants.variant_id"), nullable=False)
    cover_letter_id = Column(String(36))
    status = Column(String(30), nullable=False, default="sent")
    sent_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True))
    thread_id = Column(String(255))
    email_subject = Column(String(500))
    reply_count = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="application_log_user_job_unique"),
    )


class ScraperRun(TestBase):
    __tablename__ = "scraper_runs"
    run_id = Column(String(36), primary_key=True)
    source = Column(String(50), nullable=False)
    keywords = Column(JSON, nullable=False, default=list)
    locations = Column(JSON, nullable=False, default=list)
    pages_requested = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="queued")
    jobs_fetched = Column(Integer, nullable=False, default=0)
    jobs_inserted = Column(Integer, nullable=False, default=0)
    errors = Column(Integer, nullable=False, default=0)
    error_detail = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))


# ── Fixture: patch prod models → test models, build SQLite schema ─────────────

import orchestration.db.models as _prod_models  # noqa: E402 — must follow test model definitions


@pytest_asyncio.fixture
async def session():
    # Patch production model references so repositories use test models
    _prod_models.Job = Job
    _prod_models.MasterResume = MasterResume
    _prod_models.ResumeVariant = ResumeVariant
    _prod_models.ApplicationLog = ApplicationLog
    _prod_models.ScraperRun = ScraperRun

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_job(source="naukri", external_id="ext-001") -> JobRecord:
    return JobRecord(
        job_id=uuid.uuid4(), source=source, external_id=external_id,
        title="Python Developer", company_name="Acme Corp", company_domain="acme.com",
        location="Bangalore", remote_type="hybrid", salary_min=50000.0, salary_max=100000.0,
        experience_min=2, experience_max=5, description="Build cool stuff",
        skills_required=["Python", "FastAPI"], job_type="fulltime",
        apply_email="hr@acme.com", email_trust="verified", status="raw",
    )


def _insert_job(session, job: JobRecord) -> Job:
    row = Job(
        job_id=str(job.job_id), source=job.source, external_id=job.external_id,
        title=job.title, company_name=job.company_name, description=job.description,
        skills_required=list(job.skills_required), job_type=job.job_type,
        email_trust=job.email_trust, status=job.status, apply_email=job.apply_email,
        last_seen_at=datetime.now(timezone.utc),
    )
    session.add(row)
    return row


def _insert_resume(session) -> MasterResume:
    r = MasterResume(
        resume_id=str(uuid.uuid4()), user_id="user-1",
        file_name="resume.pdf", file_path="/tmp/resume.pdf",
    )
    session.add(r)
    return r


def _insert_variant(session, job_id, resume_id, user_id="user-1") -> ResumeVariant:
    v = ResumeVariant(
        variant_id=str(uuid.uuid4()), user_id=user_id,
        job_id=str(job_id), master_resume_id=str(resume_id),
        pdf_key="", docx_key="", cover_letter_key="", local_pdf_path="",
        s3_upload_failed=False, curated_json={}, gaps_identified=[],
        approval_status="approved", prompt_version="",
    )
    session.add(v)
    return v


# ── Job Repository ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_job_save_and_get(session):
    job = _make_job()
    _insert_job(session, job)
    await session.flush()
    fetched = await PostgresJobRepository(session).get(job.job_id)
    assert fetched.job_id == job.job_id


@pytest.mark.asyncio
async def test_job_get_not_found(session):
    with pytest.raises(JobNotFoundError):
        await PostgresJobRepository(session).get(uuid.uuid4())


@pytest.mark.asyncio
async def test_job_get_many(session):
    j1, j2 = _make_job(external_id="e1"), _make_job(external_id="e2")
    _insert_job(session, j1)
    _insert_job(session, j2)
    await session.flush()
    results = await PostgresJobRepository(session).get_many([j1.job_id, j2.job_id])
    assert len(results) == 2


@pytest.mark.asyncio
async def test_job_get_by_source(session):
    _insert_job(session, _make_job(source="naukri", external_id="n1"))
    _insert_job(session, _make_job(source="indeed", external_id="i1"))
    await session.flush()
    jobs = await PostgresJobRepository(session).get_by_source("naukri")
    assert all(j.source == "naukri" for j in jobs)


@pytest.mark.asyncio
async def test_job_get_by_status(session):
    _insert_job(session, _make_job(external_id="s1"))
    await session.flush()
    assert len(await PostgresJobRepository(session).get_by_status("raw")) >= 1


@pytest.mark.asyncio
async def test_job_count_and_exists(session):
    job = _make_job()
    _insert_job(session, job)
    await session.flush()
    repo = PostgresJobRepository(session)
    assert await repo.count() >= 1
    assert await repo.exists(job.job_id) is True
    assert await repo.exists(uuid.uuid4()) is False


@pytest.mark.asyncio
async def test_job_delete_by_source(session):
    _insert_job(session, _make_job(source="indeed", external_id="del1"))
    await session.flush()
    assert await PostgresJobRepository(session).delete_by_source("indeed") >= 1


@pytest.mark.asyncio
async def test_job_get_all_with_email(session):
    _insert_job(session, _make_job(external_id="em1"))
    await session.flush()
    jobs = await PostgresJobRepository(session).get_all_with_email()
    assert all(j.apply_email is not None for j in jobs)


# ── Variant Repository ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_variant_save_and_get(session):
    job = _make_job(external_id="vj1")
    _insert_job(session, job)
    resume = _insert_resume(session)
    await session.flush()
    variant = VariantRecord(
        variant_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        master_resume_id=uuid.UUID(resume.resume_id), pdf_key="k.pdf", docx_key="k.docx",
    )
    repo = PostgresVariantRepository(session)
    await repo.save(variant)
    await session.flush()
    assert (await repo.get(variant.variant_id)).variant_id == variant.variant_id


@pytest.mark.asyncio
async def test_variant_duplicate_raises(session):
    job = _make_job(external_id="vj2")
    _insert_job(session, job)
    resume = _insert_resume(session)
    await session.flush()
    repo = PostgresVariantRepository(session)
    v1 = VariantRecord(
        variant_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        master_resume_id=uuid.UUID(resume.resume_id), pdf_key="", docx_key="",
    )
    await repo.save(v1)
    await session.flush()
    v2 = VariantRecord(
        variant_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        master_resume_id=uuid.UUID(resume.resume_id), pdf_key="", docx_key="",
    )
    with pytest.raises(RegistryError):
        await repo.save(v2)


@pytest.mark.asyncio
async def test_variant_not_found(session):
    with pytest.raises(VariantNotFoundError):
        await PostgresVariantRepository(session).get(uuid.uuid4())


# ── Application Repository ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_application_record_send_and_get(session):
    job = _make_job(external_id="aj1")
    _insert_job(session, job)
    resume = _insert_resume(session)
    variant = _insert_variant(session, job.job_id, resume.resume_id)
    await session.flush()
    repo = PostgresApplicationRepository(session)
    app = ApplicationRecord(
        application_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        resume_variant_id=uuid.UUID(variant.variant_id),
        sent_at=datetime.now(timezone.utc),
    )
    await repo.record_send(app)
    await session.flush()
    assert (await repo.get(app.application_id)).application_id == app.application_id


@pytest.mark.asyncio
async def test_application_duplicate_raises(session):
    job = _make_job(external_id="aj2")
    _insert_job(session, job)
    resume = _insert_resume(session)
    variant = _insert_variant(session, job.job_id, resume.resume_id)
    await session.flush()
    repo = PostgresApplicationRepository(session)
    a1 = ApplicationRecord(
        application_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        resume_variant_id=uuid.UUID(variant.variant_id),
        sent_at=datetime.now(timezone.utc),
    )
    await repo.record_send(a1)
    await session.flush()
    a2 = ApplicationRecord(
        application_id=uuid.uuid4(), user_id="user-1", job_id=job.job_id,
        resume_variant_id=uuid.UUID(variant.variant_id),
        sent_at=datetime.now(timezone.utc),
    )
    with pytest.raises(RegistryError):
        await repo.record_send(a2)


@pytest.mark.asyncio
async def test_application_not_found(session):
    with pytest.raises(ApplicationNotFoundError):
        await PostgresApplicationRepository(session).get(uuid.uuid4())
