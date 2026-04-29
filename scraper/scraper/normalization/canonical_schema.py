"""Canonical job schema — unified output format."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CanonicalJob(BaseModel):
    """Unified schema for all job sources after full pipeline processing."""

    # Identifiers
    job_id: Optional[str] = None
    source: str
    external_id: str
    source_url: str

    # Core
    title: str
    company_name: str
    company_domain: Optional[str] = None
    description: str

    # Location
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: str = "India"
    remote_type: str = "unknown"

    # Compensation
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"

    # Experience
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None

    # Classification
    job_type: str = "unknown"
    skills_required: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    # Application
    apply_url: Optional[str] = None
    apply_email: Optional[str] = None
    apply_method: str = "url"

    # Timestamps
    posted_at: Optional[datetime] = None
    posted_days_ago: Optional[int] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    # Quality
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Deduplication
    content_hash: str = ""
    url_hash: str = ""
