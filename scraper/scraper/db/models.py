"""SQLAlchemy ORM models for the scraper.

Mirrors the orchestration schema for Jobs and ScraperRuns.
No foreign keys to user tables are included to keep the scraper decoupled.
"""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


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
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


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
