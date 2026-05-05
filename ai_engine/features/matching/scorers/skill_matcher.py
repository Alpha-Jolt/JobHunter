"""Semantic skill matcher — maps candidate skills to job requirements."""

from __future__ import annotations

from ai_engine.shared.text_utils import normalise_for_comparison

# Semantic equivalence groups — extend as needed
_EQUIVALENCE_GROUPS: list[set[str]] = [
    {"postgresql", "postgres", "relational database", "sql database", "rdbms"},
    {"javascript", "js", "ecmascript"},
    {"typescript", "ts"},
    {"python", "python3", "py"},
    {"react", "reactjs", "react.js"},
    {"node", "nodejs", "node.js"},
    {"machine learning", "ml", "deep learning"},
    {"aws", "amazon web services", "amazon aws"},
    {"gcp", "google cloud", "google cloud platform"},
    {"azure", "microsoft azure"},
    {"docker", "containerisation", "containerization"},
    {"kubernetes", "k8s"},
    {"ci/cd", "continuous integration", "continuous deployment"},
    {"rest", "restful", "rest api", "restful api"},
    {"nosql", "mongodb", "document database"},
]


def _find_group(skill: str) -> set[str] | None:
    """Return the equivalence group containing the skill, or None."""
    normalised = normalise_for_comparison(skill)
    for group in _EQUIVALENCE_GROUPS:
        if normalised in group:
            return group
    return None


def match_skills(
    candidate_skills: list[str],
    required_skills: list[str],
) -> tuple[list[str], list[str]]:
    """Semantically match candidate skills against job requirements.

    Args:
        candidate_skills: Skills from the parsed resume.
        required_skills: Skills required by the job.

    Returns:
        Tuple of (matched_skills, gap_skills).
        matched_skills: Required skills the candidate possesses.
        gap_skills: Required skills the candidate lacks.
    """
    normalised_candidate = {normalise_for_comparison(s) for s in candidate_skills}

    matched: list[str] = []
    gaps: list[str] = []

    for req in required_skills:
        req_norm = normalise_for_comparison(req)

        # Direct match
        if req_norm in normalised_candidate:
            matched.append(req)
            continue

        # Semantic equivalence match
        group = _find_group(req)
        if group and (group & normalised_candidate):
            matched.append(req)
            continue

        gaps.append(req)

    return matched, gaps
