"""Intermediate (raw extracted) job schema — preserves original values."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IntermediateJob(BaseModel):
    """Raw data extracted from a scraper before any cleaning."""

    # Source metadata
    source: str
    external_id: str
    raw_url: str

    # Raw extracted fields
    title: Optional[str] = None
    company_name: Optional[str] = None
    location_raw: Optional[str] = None
    salary_raw: Optional[str] = None
    experience_raw: Optional[str] = None
    job_type_raw: Optional[str] = None
    description: Optional[str] = None
    benefits_raw: Optional[List[str]] = Field(default_factory=list)
    skills_required_raw: Optional[List[str]] = Field(default_factory=list)

    # Application info
    posted_date_raw: Optional[str] = None
    company_domain: Optional[str] = None
    apply_url: Optional[str] = None
    apply_email_raw: Optional[str] = None

    # Extraction metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction_duration_ms: float = 0.0
    extraction_source: str = "html_parser"  # 'html_parser' | 'json_api'
