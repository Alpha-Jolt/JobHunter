"""Pydantic models for data collector form."""

from typing import List, Optional

from pydantic import BaseModel, Field


class JobPreferences(BaseModel):
    """User job search preferences collected via questionnaire."""

    keywords: List[str] = Field(min_length=1)
    locations: List[str] = Field(min_length=1)
    experience: Optional[str] = None  # "fresher" | "mid" | "senior"
    salary_min_lpa: Optional[float] = None
    remote_preference: Optional[str] = None  # "remote" | "hybrid" | "onsite"
    sources: List[str] = Field(default_factory=lambda: ["naukri", "indeed"])
