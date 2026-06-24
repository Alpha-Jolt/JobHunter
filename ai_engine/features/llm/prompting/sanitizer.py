"""Prompt input sanitizer — XML-encodes user-supplied content before template injection."""

from __future__ import annotations

import html

# Keys whose values originate from user-controlled sources
_USER_CONTROLLED_KEYS = frozenset({
    "job_description",
    "resume_text",
    "resume_data",
    "job_analysis",
    "comparison_result",
    "optimised_variant",
})


def sanitize_variables(variables: dict[str, str]) -> dict[str, str]:
    """XML-encode values for known user-controlled template variables.

    Only variables in _USER_CONTROLLED_KEYS are encoded; system-generated
    variables (e.g. schema instructions) are passed through unchanged.

    html.escape() converts < > & " ' to their XML entities, preventing
    injected XML tags from being interpreted as structural boundaries.

    Args:
        variables: Raw template variable dict from the calling strategy.

    Returns:
        Dict with user-controlled values XML-encoded.
    """
    return {
        k: html.escape(v) if k in _USER_CONTROLLED_KEYS else v
        for k, v in variables.items()
    }
