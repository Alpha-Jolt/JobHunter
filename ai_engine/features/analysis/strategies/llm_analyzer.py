"""LLM-based job analysis strategy."""

from __future__ import annotations

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter

logger = get_logger(__name__)


class LLMAnalyzerStrategy:
    """Analyses a job description using the LLM router.

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

    async def analyse(self, job_description: str, job_id: str = "") -> JobAnalysis:
        """Run LLM analysis on a job description.

        Args:
            job_description: Raw job description text.
            job_id: Optional job identifier for metadata.

        Returns:
            Validated JobAnalysis instance.

        Raises:
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        prompt_name = self._registry.resolve("job_analyser")
        prompt, version = self._loader.load(prompt_name, {"job_description": job_description})

        result = await self._router.complete(
            prompt=prompt,
            output_schema=JobAnalysis.output_schema(),
            prompt_version=version,
        )

        try:
            analysis = JobAnalysis(
                **result.content,
                prompt_version_used=version,
                tokens_used=result.prompt_tokens + result.completion_tokens,
                job_id=job_id,
            )
        except Exception as exc:
            raise SchemaValidationError(
                f"JobAnalysis schema validation failed: {exc}",
                context={"raw_content": result.content},
            ) from exc

        logger.info("llm_analyzer.complete", job_id=job_id, prompt_version=version)
        return analysis
