"""LLM cover letter generation strategy."""

from __future__ import annotations

import json

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant

logger = get_logger(__name__)

_COVER_LETTER_SCHEMA = {
    "type": "object",
    "properties": {
        "cover_letter_text": {"type": "string"},
        "word_count": {"type": "integer"},
    },
    "required": ["cover_letter_text"],
}


class LLMCoverLetterStrategy:
    """Generates a cover letter using the LLM router.

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

    async def generate(
        self,
        variant: OptimisedVariant,
        job_analysis: JobAnalysis,
    ) -> str:
        """Generate a cover letter for the given variant and job.

        Args:
            variant: Optimised resume variant.
            job_analysis: Analysed job description.

        Returns:
            Cover letter text string.

        Raises:
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        prompt_name = self._registry.resolve("cover_letter")
        prompt, version = self._loader.load(
            prompt_name,
            {
                "job_analysis": json.dumps(
                    job_analysis.model_dump(mode="json", exclude={"raw_text"}), indent=2
                ),
                "optimised_variant": json.dumps(variant.model_dump(mode="json"), indent=2),
                "application_tone": job_analysis.application_tone or "formal",
            },
        )

        result = await self._router.complete(
            prompt=prompt,
            output_schema=_COVER_LETTER_SCHEMA,
            prompt_version=version,
        )

        cover_letter_text = result.content.get("cover_letter_text", "")
        if not cover_letter_text:
            raise SchemaValidationError(
                "Cover letter text is empty.", context={"raw": result.content}
            )

        logger.info(
            "llm_cover_letter.complete",
            job_id=job_analysis.job_id,
            word_count=result.content.get("word_count", 0),
        )
        return cover_letter_text
