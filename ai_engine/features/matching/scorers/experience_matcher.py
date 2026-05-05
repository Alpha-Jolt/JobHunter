"""Experience matcher — maps candidate experience to job responsibilities."""

from __future__ import annotations

from ai_engine.features.resume.models.resume_schema import ExperienceEntry
from ai_engine.shared.text_utils import normalise_for_comparison


def _relevance_score(entry: ExperienceEntry, responsibilities: list[str]) -> float:
    """Score how relevant an experience entry is to a set of responsibilities.

    Uses token overlap between the entry's role/responsibilities and the job responsibilities.

    Args:
        entry: Candidate experience entry.
        responsibilities: Job key responsibilities.

    Returns:
        Float score 0.0–1.0.
    """
    entry_text = " ".join([entry.role, entry.company] + entry.responsibilities + entry.achievements)
    entry_tokens = set(normalise_for_comparison(entry_text).split())

    resp_text = " ".join(responsibilities)
    resp_tokens = set(normalise_for_comparison(resp_text).split())

    if not resp_tokens:
        return 0.0

    overlap = entry_tokens & resp_tokens
    return len(overlap) / len(resp_tokens)


def rank_experience(
    experience_entries: list[ExperienceEntry],
    key_responsibilities: list[str],
) -> list[str]:
    """Rank experience entries by relevance to job responsibilities.

    Args:
        experience_entries: Candidate's experience entries.
        key_responsibilities: Job's key responsibilities.

    Returns:
        List of relevant experience descriptions, ordered by relevance (most relevant first).
    """
    scored = [
        (entry, _relevance_score(entry, key_responsibilities)) for entry in experience_entries
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        f"{entry.role} at {entry.company}" if entry.company else entry.role
        for entry, score in scored
        if score > 0.0
    ]
