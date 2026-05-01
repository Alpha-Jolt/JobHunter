"""Sample job analyses for testing."""

from __future__ import annotations

from ai_engine.features.analysis.models.job_analysis import JobAnalysis

SAMPLE_JOB_ANALYSIS = JobAnalysis(
    required_skills=["Python", "PostgreSQL", "Docker", "REST APIs"],
    preferred_skills=["Kubernetes", "AWS"],
    experience_level="senior",
    role_clarity_score=4,
    key_responsibilities=["Build scalable backend services", "Mentor junior developers"],
    implied_values=["engineering excellence", "collaboration"],
    red_flag_signals=[],
    application_tone="formal",
    prompt_version_used="job_analyser_v1",
    tokens_used=300,
    job_id="job-001",
)
