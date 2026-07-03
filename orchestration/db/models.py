"""SQLAlchemy ORM models for JobHunter Phase 0+ PostgreSQL schema."""

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ── Auth models ───────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone = Column(String(20))
    role = Column(Enum("hunter", "mentor", "recruiter", "admin", name="user_role"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    token_hash = Column(String(255), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "token_hash", name="refresh_tokens_user_hash_unique"),
    )

    user = relationship("User", back_populates="refresh_tokens")


# ── Job models ────────────────────────────────────────────────────────────────

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    skills_required = Column(ARRAY(Text), nullable=False, default=list)
    job_type = Column(String(20), nullable=False, default="fulltime")
    apply_email = Column(String(255))
    email_trust = Column(String(20), nullable=False, default="unknown")
    apply_url = Column(Text)
    posted_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False, default="raw")
    recruiter_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="jobs_source_external_id_unique"),
        CheckConstraint("status IN ('raw','reviewed','applied','closed')", name="ck_jobs_status"),
        CheckConstraint(
            "email_trust IN ('unknown','verified','low')", name="ck_jobs_email_trust"
        ),
        CheckConstraint(
            "remote_type IS NULL OR remote_type IN ('onsite','hybrid','remote')",
            name="ck_jobs_remote_type",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
    )

    variants = relationship("ResumeVariant", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("ApplicationLog", back_populates="job")
    cover_letters = relationship("CoverLetter", back_populates="job")


class MasterResume(Base):
    __tablename__ = "master_resumes"

    resume_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    parsed_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    variants = relationship("ResumeVariant", back_populates="master_resume")


class ResumeVariant(Base):
    __tablename__ = "resume_variants"

    variant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(
        UUID(as_uuid=True), ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
    )
    master_resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.resume_id", ondelete="RESTRICT"),
        nullable=False,
    )
    pdf_key = Column(Text, nullable=False, default="")
    docx_key = Column(Text, nullable=False, default="")
    cover_letter_key = Column(Text, nullable=False, default="")
    local_pdf_path = Column(Text, nullable=False, default="")
    s3_upload_failed = Column(Boolean, nullable=False, default=False)
    curated_json = Column(JSONB, nullable=False, default=dict)
    gaps_identified = Column(ARRAY(Text), nullable=False, default=list)
    approval_status = Column(String(20), nullable=False, default="pending")
    approval_token = Column(String(128))
    approved_at = Column(DateTime(timezone=True))
    user_feedback = Column(Text)
    prompt_version = Column(String(50), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="resume_variants_user_job_unique"),
        CheckConstraint(
            "approval_status IN ('pending','approved','rejected')",
            name="ck_variants_approval_status",
        ),
    )

    job = relationship("Job", back_populates="variants")
    master_resume = relationship("MasterResume", back_populates="variants")
    applications = relationship("ApplicationLog", back_populates="resume_variant")
    cover_letters = relationship("CoverLetter", back_populates="variant")


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    cover_letter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(
        UUID(as_uuid=True), ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resume_variants.variant_id", ondelete="SET NULL"),
    )
    content_text = Column(Text, nullable=False)
    file_key = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    job = relationship("Job", back_populates="cover_letters")
    variant = relationship("ResumeVariant", back_populates="cover_letters")
    applications = relationship("ApplicationLog", back_populates="cover_letter")


class ApplicationLog(Base):
    __tablename__ = "application_log"

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(
        UUID(as_uuid=True), ForeignKey("jobs.job_id", ondelete="RESTRICT"), nullable=False
    )
    resume_variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resume_variants.variant_id", ondelete="RESTRICT"),
        nullable=False,
    )
    cover_letter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cover_letters.cover_letter_id", ondelete="SET NULL"),
    )
    status = Column(String(30), nullable=False, default="sent")
    sent_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True))
    thread_id = Column(String(255))
    email_subject = Column(String(500))
    reply_count = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="application_log_user_job_unique"),
        CheckConstraint(
            "status IN ('sent','replied','interview_scheduled','rejected','ghosted')",
            name="ck_application_status",
        ),
        CheckConstraint("reply_count >= 0", name="ck_application_reply_count"),
    )

    job = relationship("Job", back_populates="applications")
    resume_variant = relationship("ResumeVariant", back_populates="applications")
    cover_letter = relationship("CoverLetter", back_populates="applications")


class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    keywords = Column(ARRAY(Text), nullable=False, default=list)
    locations = Column(ARRAY(Text), nullable=False, default=list)
    pages_requested = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="queued")
    jobs_fetched = Column(Integer, nullable=False, default=0)
    jobs_inserted = Column(Integer, nullable=False, default=0)
    errors = Column(Integer, nullable=False, default=0)
    error_detail = Column(Text)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','completed','failed')", name="ck_scraper_run_status"
        ),
        CheckConstraint("jobs_fetched >= 0", name="ck_scraper_jobs_fetched"),
        CheckConstraint("jobs_inserted >= 0", name="ck_scraper_jobs_inserted"),
        CheckConstraint("errors >= 0", name="ck_scraper_errors"),
    )



# ── Company Discovery models ──────────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(500), nullable=True)
    normalized_name = Column(String(500), nullable=True)
    apex_domain = Column(String(255), nullable=False)
    subdomains = Column(ARRAY(Text), nullable=False, default=list)
    career_page_url = Column(Text, nullable=True)
    career_emails = Column(ARRAY(Text), nullable=False, default=list)
    contact_emails = Column(ARRAY(Text), nullable=False, default=list)
    email_trust = Column(String(20), nullable=False, default="unverified")
    ats_platform = Column(String(50), nullable=False, default="none")
    industry = Column(String(255), nullable=True)
    hq_location = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)
    source_detail = Column(Text, nullable=True)
    robots_txt_allowed = Column(Boolean, nullable=True)
    discovery_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_enriched_at = Column(DateTime(timezone=True), nullable=True)
    email_last_crawled_at = Column(DateTime(timezone=True), nullable=True)
    crawl_status = Column(String(20), nullable=False, default="pending")
    dedup_fingerprint = Column(String(64), nullable=False)
    related_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.company_id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("apex_domain", name="companies_apex_domain_unique"),
        UniqueConstraint("dedup_fingerprint", name="companies_dedup_fingerprint_unique"),
        CheckConstraint(
            "email_trust IN ('unverified', 'low_trust')",
            name="ck_companies_email_trust",
        ),
        CheckConstraint(
            "ats_platform IN ('greenhouse','lever','ashby','workday','smartrecruiters',"
            "'bamboohr','teamtailor','recruitee','jazzhr','workable','custom','none')",
            name="ck_companies_ats_platform",
        ),
        CheckConstraint(
            "crawl_status IN ('pending','enriched','failed','robots_blocked','access_denied','name_only')",
            name="ck_companies_crawl_status",
        ),
        CheckConstraint(
            "source IN ('bootstrap_dataset','govt_registry','vc_portfolio','github_org',"
            "'directory','search_discovery','recursive')",
            name="ck_companies_source",
        ),
    )

    career_jobs = relationship(
        "CareerJob", back_populates="company", cascade="all, delete-orphan"
    )
    related_company = relationship("Company", remote_side="Company.company_id")


class CareerJob(Base):
    __tablename__ = "career_jobs"

    career_job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.company_id", ondelete="CASCADE"),
        nullable=False,
    )
    job_title = Column(String(500), nullable=False)
    job_url = Column(Text, nullable=False)
    url_hash = Column(String(64), nullable=False)
    content_hash = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    skills_required = Column(ARRAY(Text), nullable=False, default=list)
    location = Column(String(255), nullable=True)
    remote_type = Column(String(20), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    experience_min = Column(Integer, nullable=True)
    experience_max = Column(Integer, nullable=True)
    job_type = Column(String(20), nullable=True)
    apply_email = Column(String(255), nullable=True)
    apply_url = Column(Text, nullable=True)
    ats_platform = Column(String(50), nullable=True)
    extraction_method = Column(String(30), nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status = Column(String(20), nullable=False, default="raw")
    source_channel = Column(String(30), nullable=False, default="career_page")

    __table_args__ = (
        UniqueConstraint(
            "company_id", "url_hash", name="career_jobs_company_url_unique"
        ),
        CheckConstraint(
            "remote_type IS NULL OR remote_type IN ('onsite','hybrid','remote')",
            name="ck_career_jobs_remote_type",
        ),
        CheckConstraint(
            "job_type IS NULL OR job_type IN ('fulltime','parttime','contract','internship','freelance')",
            name="ck_career_jobs_job_type",
        ),
        CheckConstraint(
            "extraction_method IN ('ats_api','json_ld','sitemap','api_reverse','html_parse','playwright_render')",
            name="ck_career_jobs_extraction_method",
        ),
        CheckConstraint(
            "status IN ('active','closed','raw')",
            name="ck_career_jobs_status",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_career_jobs_salary_range",
        ),
    )

    company = relationship("Company", back_populates="career_jobs")
