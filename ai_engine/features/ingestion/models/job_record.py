"""JobRecord — internal data model for a single job listing."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class JobRecord(BaseModel):
    """Normalised representation of a scraped job listing.

    All downstream modules consume this model. Fields map from scraper CSV/JSON output.
    """

    job_id: str = Field(description="Unique identifier for the job listing.")
    source: str = Field(description="Scraper source name (e.g. 'indeed', 'naukri').")
    title: str = Field(description="Job title.")
    company: str = Field(description="Hiring company name.")
    location: str = Field(default="", description="Job location string.")
    remote_type: str = Field(default="", description="Remote/hybrid/onsite indicator.")
    experience_level: str = Field(default="", description="Required experience level.")
    description: str = Field(description="Full job description text.")
    skills_required: list[str] = Field(
        default_factory=list, description="Extracted required skills."
    )
    apply_email: str = Field(default="", description="Application email address if present.")
    apply_url: str = Field(default="", description="Application URL.")
    posted_at: datetime | None = Field(default=None, description="Job posting timestamp.")
    scraped_at: datetime | None = Field(default=None, description="Scrape timestamp.")

    # Phase 0+ optimisation: pre-computed analysis can be attached
    pre_computed_analysis: dict | None = Field(
        default=None,
        description="Optional pre-computed JobAnalysis dict to skip re-analysis.",
    )

    model_config = {"frozen": True}
