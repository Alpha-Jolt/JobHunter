"""Prompt adjuster — Phase 0+ hook for user feedback refinement."""

from __future__ import annotations


def adjust_prompt_for_feedback(base_prompt: str, user_feedback: str) -> str:
    """Append user feedback as an additional instruction to the base prompt.

    This is a Phase 0+ hook. In Phase 0, it is not called by the pipeline.
    When user feedback loops are implemented, this function refines the
    optimiser prompt without modifying the base prompt file.

    Args:
        base_prompt: The rendered base optimiser prompt.
        user_feedback: User's rejection reason or refinement request.

    Returns:
        Adjusted prompt with feedback appended.
    """
    return (
        f"{base_prompt}\n\n" f"ADDITIONAL USER FEEDBACK (apply to this revision):\n{user_feedback}"
    )
