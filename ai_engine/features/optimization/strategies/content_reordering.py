"""Deterministic content reordering — no LLM involved."""

from __future__ import annotations

from ai_engine.features.resume.models.resume_schema import ExperienceEntry
from ai_engine.shared.text_utils import normalise_for_comparison


def reorder_experience(
    experience_entries: list[ExperienceEntry],
    key_responsibilities: list[str],
) -> list[ExperienceEntry]:
    """Reorder experience entries by relevance to job responsibilities.

    Deterministic — uses token overlap scoring, no LLM.

    Args:
        experience_entries: Candidate's experience entries.
        key_responsibilities: Job's key responsibilities.

    Returns:
        Reordered list of ExperienceEntry (most relevant first).
    """
    resp_tokens = set(normalise_for_comparison(" ".join(key_responsibilities)).split())

    def score(entry: ExperienceEntry) -> float:
        text = " ".join([entry.role] + entry.responsibilities + entry.achievements)
        tokens = set(normalise_for_comparison(text).split())
        if not resp_tokens:
            return 0.0
        return len(tokens & resp_tokens) / len(resp_tokens)

    return sorted(experience_entries, key=score, reverse=True)


def reorder_bullets(bullets: list[str], key_responsibilities: list[str]) -> list[str]:
    """Reorder bullet points by relevance to job responsibilities.

    Args:
        bullets: List of bullet point strings.
        key_responsibilities: Job's key responsibilities.

    Returns:
        Reordered bullet list (most relevant first).
    """
    resp_tokens = set(normalise_for_comparison(" ".join(key_responsibilities)).split())

    def score(bullet: str) -> float:
        tokens = set(normalise_for_comparison(bullet).split())
        if not resp_tokens:
            return 0.0
        return len(tokens & resp_tokens) / len(resp_tokens)

    return sorted(bullets, key=score, reverse=True)
