"""LLM-based comparison strategy."""

from __future__ import annotations

import json

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.resume.models.resume_schema import ResumeData

logger = get_logger(__name__)


class LLMComparisonStrategy:
    """Compares resume against job analysis using the LLM router.

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

    async def compare(
        self,
        resume: ResumeData,
        job_analysis: JobAnalysis,
    ) -> ComparisonResult:
        """Run LLM comparison between resume and job analysis.

        Args:
            resume: Parsed resume data.
            job_analysis: Analysed job description.

        Returns:
            Validated ComparisonResult.

        Raises:
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        prompt_name = self._registry.resolve("comparison_engine")
        prompt, version = self._loader.load(
            prompt_name,
            {
                "job_analysis": json.dumps(
                    job_analysis.model_dump(mode="json", exclude={"raw_text"}), indent=2
                ),
                "resume_data": json.dumps(
                    resume.model_dump(mode="json", exclude={"raw_text"}), indent=2
                ),
            },
        )

        result = await self._router.complete(
            prompt=prompt,
            output_schema=ComparisonResult.output_schema(),
            prompt_version=version,
        )

        try:
            comparison = ComparisonResult(
                **result.content,
                prompt_version_used=version,
                job_id=job_analysis.job_id,
            )
        except Exception as exc:
            raise SchemaValidationError(
                f"ComparisonResult schema validation failed: {exc}",
                context={"raw_content": result.content},
            ) from exc

        logger.info(
            "llm_comparison.complete",
            job_id=job_analysis.job_id,
            match_score=comparison.match_score,
            prompt_version=version,
        )
        return comparison
