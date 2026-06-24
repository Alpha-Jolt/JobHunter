"""Prompt cache manager — splits prompts at the user-data boundary for Anthropic caching."""

from __future__ import annotations

from dataclasses import dataclass

_USER_DATA_OPEN = "<user_data>"


@dataclass
class CachedPromptParts:
    """Prompt split into a cacheable preamble and a fresh user-data section."""

    preamble: str      # Everything before <user_data> — eligible for caching
    user_content: str  # Everything from <user_data> onward — always fresh


def split_prompt(rendered_prompt: str) -> CachedPromptParts:
    """Split a rendered prompt at the first <user_data> tag.

    If no <user_data> tag exists, the whole prompt is the preamble
    (cacheable) with an empty user section.

    Args:
        rendered_prompt: Fully substituted prompt string.

    Returns:
        CachedPromptParts with preamble and user_content.
    """
    idx = rendered_prompt.find(_USER_DATA_OPEN)
    if idx == -1:
        return CachedPromptParts(preamble=rendered_prompt, user_content="")
    return CachedPromptParts(
        preamble=rendered_prompt[:idx].rstrip(),
        user_content=rendered_prompt[idx:],
    )
