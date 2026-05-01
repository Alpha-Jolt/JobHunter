"""ComparisonResult — output schema for resume-job matching."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ComparisonResult(BaseModel):
    """Structured result of comparing a resume against a job analysis."""

    match_score: int = Field(default=0, ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    gap_skills: list[str] = Field(default_factory=list)
    matched_experience: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    strength_summary: str = ""

    # Metadata
    comparison_timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt_version_used: str = ""
    job_id: str = ""

    model_config = {"frozen": True}

    @classmethod
    def output_schema(cls) -> dict:
        """Return the JSON Schema used as LLM output contract."""
        return {
            "type": "object",
            "properties": {
                "match_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "matched_skills": {"type": "array", "items": {"type": "string"}},
                "gap_skills": {"type": "array", "items": {"type": "string"}},
                "matched_experience": {"type": "array", "items": {"type": "string"}},
                "weak_points": {"type": "array", "items": {"type": "string"}},
                "strength_summary": {"type": "string"},
            },
            "required": ["match_score", "matched_skills", "gap_skills"],
        }
