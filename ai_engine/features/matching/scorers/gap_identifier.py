"""Gap identifier — identifies missing skills and weak experience areas."""

from __future__ import annotations

from ai_engine.features.resume.models.resume_schema import ResumeData
from ai_engine.shared.text_utils import normalise_for_comparison


def identify_weak_points(
    resume: ResumeData,
    gap_skills: list[str],
    required_skills: list[str],
) -> list[str]:
    """Identify skills the candidate has but with insufficient depth.

    A skill is considered 'weak' if it appears in the resume but is not
    backed by any experience entry mentioning it.

    Args:
        resume: Parsed resume data.
        gap_skills: Skills the candidate is missing entirely.
        required_skills: All required skills from the job.

    Returns:
        List of weak skill descriptions.
    """
    gap_set = {normalise_for_comparison(s) for s in gap_skills}
    experience_text = " ".join(
        " ".join(e.responsibilities + e.achievements) for e in resume.experience_entries
    )
    experience_tokens = set(normalise_for_comparison(experience_text).split())

    weak: list[str] = []
    for skill in required_skills:
        skill_norm = normalise_for_comparison(skill)
        if skill_norm in gap_set:
            continue  # Already a gap, not a weak point
        # Skill is present in resume.skills but not backed by experience
        skill_tokens = set(skill_norm.split())
        if not (skill_tokens & experience_tokens):
            weak.append(f"{skill} (listed but not demonstrated in experience)")

    return weak
