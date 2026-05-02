"""Variable mapper — maps structured data to email template slots."""

from __future__ import annotations

from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant


def map_email_variables(
    job_analysis: JobAnalysis,
    variant: OptimisedVariant,
    job_title: str = "",
    company: str = "",
) -> dict[str, str]:
    """Map JobAnalysis and OptimisedVariant data to email template variables.

    Only maps data that exists — does not generate or invent content.
    Missing data results in an empty string for that slot.

    Args:
        job_analysis: Analysed job description.
        variant: Optimised resume variant.
        job_title: Job title string.
        company: Company name string.

    Returns:
        Dict of template variable name → value.
    """
    top_skills = ", ".join(variant.prioritized_skills[:5]) if variant.prioritized_skills else ""
    top_experience = (
        f"{variant.reordered_experience[0].role} at {variant.reordered_experience[0].company}"
        if variant.reordered_experience
        else ""
    )

    return {
        "job_title": job_title,
        "company": company,
        "top_skills": top_skills,
        "relevant_experience": top_experience,
        "application_tone": job_analysis.application_tone,
        "gaps_acknowledged": ", ".join(variant.gaps[:3]) if variant.gaps else "",
    }
