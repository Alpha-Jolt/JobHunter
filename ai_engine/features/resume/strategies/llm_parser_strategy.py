"""LLM-based resume parsing strategy."""

from __future__ import annotations

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter
from ai_engine.features.resume.models.resume_schema import (
    EducationEntry,
    ExperienceEntry,
    PersonalInfo,
    ProjectEntry,
    ResumeData,
)

logger = get_logger(__name__)


class LLMParserStrategy:
    """Parses resume text into structured ResumeData using the LLM router.

    Args:
        router: Configured LLMRouter instance.
        prompt_loader: PromptLoader for rendering prompts.
        prompt_registry: PromptRegistry for version resolution.
    """

    def __init__(
        self,
        router: LLMRouter,
        prompt_loader: PromptLoader,
        prompt_registry: PromptRegistry,
    ) -> None:
        self._router = router
        self._loader = prompt_loader
        self._registry = prompt_registry

    async def parse(self, cleaned_text: str) -> tuple[ResumeData, str]:
        """Parse cleaned resume text into ResumeData.

        Args:
            cleaned_text: Cleaned resume text from the extractor pipeline.

        Returns:
            Tuple of (ResumeData, prompt_version_used).

        Raises:
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        prompt_name = self._registry.resolve("resume_parser")
        prompt, version = self._loader.load(prompt_name, {"resume_text": cleaned_text})

        result = await self._router.complete(
            prompt=prompt,
            output_schema=ResumeData.output_schema(),
            prompt_version=version,
        )

        try:
            content = result.content
            resume = ResumeData(
                personal=PersonalInfo(**content.get("personal", {})),
                summary=content.get("summary", ""),
                experience_entries=[
                    ExperienceEntry(**e) for e in content.get("experience_entries", [])
                ],
                education=[EducationEntry(**e) for e in content.get("education", [])],
                skills=content.get("skills", []),
                certifications=content.get("certifications", []),
                projects=[ProjectEntry(**p) for p in content.get("projects", [])],
                raw_text=cleaned_text,
            )
        except Exception as exc:
            raise SchemaValidationError(
                f"ResumeData schema validation failed: {exc}",
                context={"raw_content": result.content},
            ) from exc

        logger.info("llm_parser.complete", prompt_version=version, skills_count=len(resume.skills))
        return resume, version
