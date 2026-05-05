"""Sample job records for testing."""

from __future__ import annotations

from ai_engine.features.ingestion.models.job_record import JobRecord

SAMPLE_JOB_CLEAR = JobRecord(
    job_id="job-001",
    source="indeed",
    title="Senior Python Developer",
    company="TechCorp",
    location="Remote",
    remote_type="remote",
    experience_level="senior",
    description=(
        "We are looking for a Senior Python Developer with 5+ years of experience. "
        "Required skills: Python, PostgreSQL, Docker, REST APIs. "
        "Preferred: Kubernetes, AWS. "
        "Responsibilities: Build scalable backend services, mentor junior developers. "
        "Salary: $120k-$150k. Apply at careers@techcorp.com"
    ),
    skills_required=["Python", "PostgreSQL", "Docker", "REST APIs"],
    apply_email="careers@techcorp.com",
    apply_url="https://techcorp.com/jobs/001",
)

SAMPLE_JOB_VAGUE = JobRecord(
    job_id="job-002",
    source="naukri",
    title="Developer",
    company="StartupXYZ",
    description=(
        "We need a developer who is passionate about technology and can work "
        "in a fast-paced environment. Must be a team player. Competitive salary. "
        "Responsibilities: Various development tasks as assigned."
    ),
    skills_required=[],
    apply_url="https://startupxyz.com/apply",
)

ALL_SAMPLE_JOBS = [SAMPLE_JOB_CLEAR, SAMPLE_JOB_VAGUE]
