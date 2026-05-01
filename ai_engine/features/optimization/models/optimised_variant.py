"""OptimisedVariant — schema for a tailored resume variant."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai_engine.features.resume.models.resume_schema import ExperienceEntry, ProjectEntry


class OptimisedVariant(BaseModel):
    """A tailored resume variant produced by the optimiser.

    All content must be traceable back to the source ResumeData.
    """

    reordered_experience: list[ExperienceEntry] = Field(default_factory=list)
    rewritten_summary: str = ""
    prioritized_skills: list[str] = Field(default_factory=list)
    selected_projects: list[ProjectEntry] = Field(default_factory=list)
    selected_certifications: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(
        default_factory=list, description="Skills/experience the candidate lacks."
    )

    # Metadata
    prompt_version_used: str = ""
    job_id: str = ""
    source_resume_hash: str = Field(
        default="", description="Hash of source ResumeData for traceability."
    )

    model_config = {"frozen": True}

    @classmethod
    def output_schema(cls) -> dict:
        """Return the JSON Schema used as LLM output contract."""
        return {
            "type": "object",
            "properties": {
                "reordered_experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "role": {"type": "string"},
                            "duration": {"type": "string"},
                            "responsibilities": {"type": "array", "items": {"type": "string"}},
                            "achievements": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "rewritten_summary": {"type": "string"},
                "prioritized_skills": {"type": "array", "items": {"type": "string"}},
                "selected_projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "technologies": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "selected_certifications": {"type": "array", "items": {"type": "string"}},
                "gaps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["reordered_experience", "prioritized_skills", "gaps"],
        }
