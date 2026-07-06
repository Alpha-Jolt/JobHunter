"""SQLAlchemy ORM models and Pydantic request schemas for company discovery.

ORM models map to the shared `companies` and `career_jobs` tables created by
the orchestration Alembic migrations. Pydantic models handle request validation.
"""

import uuid

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from core.db import Base
from typing import List, Optional


# ── SQLAlchemy ORM models ─────────────────────────────────────────────────────

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


# ── Pydantic request schemas ──────────────────────────────────────────────────

class StartDiscoveryRequest(BaseModel):
    role: str
    location: str
    experience: str = "fresher"
    salary: Optional[str] = None


class BootstrapRequest(BaseModel):
    sources: List[str] = ["all"]


class StartCareerScrapeRequest(BaseModel):
    company_id: Optional[uuid.UUID] = None
