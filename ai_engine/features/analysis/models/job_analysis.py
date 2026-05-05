"""JobAnalysis — output schema for job description analysis."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class JobAnalysis(BaseModel):
    """Structured analysis of a job description produced by the LLM analyser."""

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_level: str = Field(default="")
    role_clarity_score: int = Field(default=3, ge=1, le=5)
    key_responsibilities: list[str] = Field(default_factory=list)
    implied_values: list[str] = Field(default_factory=list)
    red_flag_signals: list[str] = Field(default_factory=list)
    application_tone: str = Field(default="formal")

    # Metadata
    analysis_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prompt_version_used: str = Field(default="")
    tokens_used: int = Field(default=0)
    job_id: str = Field(default="")

    # Phase 2 hook — populated by heuristics in Phase 2
    confidence_score: float | None = Field(default=None)

    model_config = {"frozen": True}

    @classmethod
    def output_schema(cls) -> dict:
        """Return the JSON Schema used as LLM output contract."""
        return {
            "type": "object",
            "properties": {
                "required_skills": {"type": "array", "items": {"type": "string"}},
                "preferred_skills": {"type": "array", "items": {"type": "string"}},
                "experience_level": {"type": "string"},
                "role_clarity_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "key_responsibilities": {"type": "array", "items": {"type": "string"}},
                "implied_values": {"type": "array", "items": {"type": "string"}},
                "red_flag_signals": {"type": "array", "items": {"type": "string"}},
                "application_tone": {"type": "string"},
            },
            "required": ["required_skills", "experience_level", "key_responsibilities"],
        }
