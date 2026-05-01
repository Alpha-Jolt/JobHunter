"""LLM-based resume optimiser strategy."""

from __future__ import annotations

import json

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.resume.models.resume_schema import ExperienceEntry, ProjectEntry, ResumeData

logger = get_logger(__name__)


class LLMOptimiserStrategy:
    """Optimises a resume for a specific job using the LLM router.

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

    async def optimise(
        self,
        resume: ResumeData,
        job_analysis: JobAnalysis,
        comparison: ComparisonResult,
    ) -> OptimisedVariant:
        """Generate an optimised resume variant.

        Args:
            resume: Source ResumeData (immutable — never modified).
            job_analysis: Analysed job description.
            comparison: Comparison result for this resume-job pair.

        Returns:
            OptimisedVariant with reordered/rephrased content.

        Raises:
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        prompt_name = self._registry.resolve("resume_optimiser")
        prompt, version = self._loader.load(
            prompt_name,
            {
                "job_analysis": json.dumps(
                    job_analysis.model_dump(mode="json", exclude={"raw_text"}), indent=2
                ),
                "comparison_result": json.dumps(comparison.model_dump(mode="json"), indent=2),
                "resume_data": json.dumps(
                    resume.model_dump(mode="json", exclude={"raw_text"}), indent=2
                ),
            },
        )

        result = await self._router.complete(
            prompt=prompt,
            output_schema=OptimisedVariant.output_schema(),
            prompt_version=version,
        )

        try:
            content = result.content
            variant = OptimisedVariant(
                reordered_experience=[
                    ExperienceEntry(**e) for e in content.get("reordered_experience", [])
                ],
                rewritten_summary=content.get("rewritten_summary", ""),
                prioritized_skills=content.get("prioritized_skills", []),
                selected_projects=[ProjectEntry(**p) for p in content.get("selected_projects", [])],
                selected_certifications=content.get("selected_certifications", []),
                gaps=content.get("gaps", []),
                prompt_version_used=version,
                job_id=job_analysis.job_id,
            )
        except Exception as exc:
            raise SchemaValidationError(
                f"OptimisedVariant schema validation failed: {exc}",
                context={"raw_content": result.content},
            ) from exc

        logger.info(
            "llm_optimiser.complete",
            job_id=job_analysis.job_id,
            skills_count=len(variant.prioritized_skills),
            gaps_count=len(variant.gaps),
            prompt_version=version,
        )
        return variant
