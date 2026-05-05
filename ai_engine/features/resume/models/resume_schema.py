"""ResumeData — schema for parsed resume content."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Candidate personal/contact information."""

    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""


class ExperienceEntry(BaseModel):
    """A single work experience entry."""

    company: str = ""
    role: str = ""
    duration: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    """A single education entry."""

    institution: str = ""
    degree: str = ""
    field: str = ""
    year: str = ""


class ProjectEntry(BaseModel):
    """A single project entry."""

    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    """Complete parsed resume data.

    The ``raw_text`` field preserves the original extracted text for
    cross-validation by the FabricationDetector. It is never modified.
    """

    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    experience_entries: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)

    # Immutable source text — used by FabricationDetector
    raw_text: str = Field(
        default="", description="Original extracted text. Never modified after parsing."
    )

    model_config = {"frozen": True}

    @classmethod
    def output_schema(cls) -> dict:
        """Return the JSON Schema used as LLM output contract."""
        return {
            "type": "object",
            "properties": {
                "personal": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "linkedin": {"type": "string"},
                        "github": {"type": "string"},
                        "portfolio": {"type": "string"},
                    },
                },
                "summary": {"type": "string"},
                "experience_entries": {
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
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution": {"type": "string"},
                            "degree": {"type": "string"},
                            "field": {"type": "string"},
                            "year": {"type": "string"},
                        },
                    },
                },
                "skills": {"type": "array", "items": {"type": "string"}},
                "certifications": {"type": "array", "items": {"type": "string"}},
                "projects": {
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
            },
            "required": ["personal", "skills", "experience_entries"],
        }
