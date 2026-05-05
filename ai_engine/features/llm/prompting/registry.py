"""Prompt registry — tracks available prompt versions and validates usage."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.exceptions import PromptNotFoundError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)

# Maps logical prompt key → list of available versions (latest first)
_PROMPT_VERSIONS: dict[str, list[str]] = {
    "job_analyser": ["job_analyser_v1"],
    "resume_parser": ["resume_parser_v1"],
    "comparison_engine": ["comparison_engine_v1"],
    "resume_optimiser": ["resume_optimiser_v1"],
    "cover_letter": ["cover_letter_v1"],
}


class PromptRegistry:
    """Registry for prompt versioning and validation.

    Args:
        prompts_dir: Path to the prompts directory.
    """

    def __init__(self, prompts_dir: Path) -> None:
        self._prompts_dir = prompts_dir

    def resolve(self, key: str, version: str | None = None) -> str:
        """Resolve a prompt key to a versioned filename.

        Args:
            key: Logical prompt key (e.g. 'job_analyser').
            version: Specific version name; uses latest if None.

        Returns:
            Versioned prompt filename (without extension).

        Raises:
            PromptNotFoundError: If key or version is not registered.
        """
        versions = _PROMPT_VERSIONS.get(key)
        if not versions:
            raise PromptNotFoundError(key)

        if version is None:
            resolved = versions[0]
        elif version in versions:
            resolved = version
        else:
            raise PromptNotFoundError(f"{key}:{version}")

        path = self._prompts_dir / f"{resolved}.txt"
        if not path.exists():
            raise PromptNotFoundError(resolved)

        logger.debug("prompt_registry.resolved", key=key, resolved=resolved)
        return resolved

    def list_versions(self, key: str) -> list[str]:
        """Return all registered versions for a prompt key.

        Args:
            key: Logical prompt key.

        Returns:
            List of version names.

        Raises:
            PromptNotFoundError: If key is not registered.
        """
        versions = _PROMPT_VERSIONS.get(key)
        if versions is None:
            raise PromptNotFoundError(key)
        return list(versions)
