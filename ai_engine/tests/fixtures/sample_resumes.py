"""Sample resume data for testing."""

from __future__ import annotations

from ai_engine.features.resume.models.resume_schema import (
    EducationEntry,
    ExperienceEntry,
    PersonalInfo,
    ResumeData,
)

SAMPLE_RESUME_TEXT = (
    "John Doe\njohn@example.com | +1-555-0100\n\n"
    "SUMMARY\nExperienced Python developer with 6 years building backend systems.\n\n"
    "EXPERIENCE\nSenior Developer at TechCorp (2020-2024)\n"
    "- Built REST APIs using Python and FastAPI\n"
    "- Managed PostgreSQL databases\n"
    "- Deployed services with Docker\n\n"
    "SKILLS\nPython, PostgreSQL, Docker, FastAPI, REST APIs, Git\n\n"
    "EDUCATION\nB.Sc. Computer Science, State University, 2018"
)

SAMPLE_RESUME = ResumeData(
    personal=PersonalInfo(name="John Doe", email="john@example.com", phone="+1-555-0100"),
    summary="Experienced Python developer with 6 years building backend systems.",
    experience_entries=[
        ExperienceEntry(
            company="TechCorp",
            role="Senior Developer",
            duration="2020-2024",
            responsibilities=[
                "Built REST APIs using Python and FastAPI",
                "Managed PostgreSQL databases",
            ],
            achievements=["Deployed services with Docker"],
        )
    ],
    education=[
        EducationEntry(
            institution="State University", degree="B.Sc.", field="Computer Science", year="2018"
        )
    ],
    skills=["Python", "PostgreSQL", "Docker", "FastAPI", "REST APIs", "Git"],
    certifications=[],
    projects=[],
    raw_text=SAMPLE_RESUME_TEXT,
)
