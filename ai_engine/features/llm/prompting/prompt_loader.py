"""Prompt loader — loads versioned prompts from disk and substitutes variables."""

from __future__ import annotations

from pathlib import Path
from string import Template

from ai_engine.core.exceptions import PromptNotFoundError


class PromptLoader:
    """Loads prompt templates from the prompts directory and renders them.

    Prompts are plain text files using Python's ``string.Template`` syntax
    (``$variable`` or ``${variable}``).

    Args:
        prompts_dir: Path to the directory containing prompt ``.txt`` files.
    """

    def __init__(self, prompts_dir: Path) -> None:
        self._prompts_dir = prompts_dir

    def load(self, name: str, variables: dict[str, str] | None = None) -> tuple[str, str]:
        """Load and render a prompt by name.

        Args:
            name: Prompt name without extension (e.g. 'job_analyser_v1').
            variables: Dict of variable substitutions.

        Returns:
            Tuple of (rendered_prompt, version_tag).

        Raises:
            PromptNotFoundError: If the prompt file does not exist.
        """
        path = self._prompts_dir / f"{name}.txt"
        if not path.exists():
            raise PromptNotFoundError(name)

        raw = path.read_text(encoding="utf-8")
        rendered = Template(raw).safe_substitute(variables or {})
        return rendered, name

    def list_available(self) -> list[str]:
        """Return names of all available prompt files (without extension).

        Returns:
            Sorted list of prompt names.
        """
        return sorted(p.stem for p in self._prompts_dir.glob("*.txt"))
