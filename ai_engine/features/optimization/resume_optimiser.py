"""Resume optimiser orchestrator."""

from __future__ import annotations

import hashlib
import json

from ai_engine.core.exceptions import FabricationDetectedError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.optimization.strategies.llm_optimiser_strategy import LLMOptimiserStrategy
from ai_engine.features.optimization.validators.fabrication_validator import validate_variant
from ai_engine.features.resume.models.resume_schema import ResumeData

logger = get_logger(__name__)


def _hash_resume(resume: ResumeData) -> str:
    """Compute a stable hash of the resume for traceability."""
    content = json.dumps(resume.model_dump(exclude={"raw_text"}), sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


class ResumeOptimiser:
    """Orchestrates resume optimisation with fabrication validation.

    Pipeline: LLM optimise → validate schema → fabrication check → return variant.

    Args:
        strategy: LLMOptimiserStrategy instance.
    """

    def __init__(self, strategy: LLMOptimiserStrategy) -> None:
        self._strategy = strategy

    async def optimise(
        self,
        resume: ResumeData,
        job_analysis: JobAnalysis,
        comparison: ComparisonResult,
    ) -> OptimisedVariant:
        """Generate and validate an optimised resume variant.

        The source ResumeData is never modified. The variant is built from a
        separate LLM-generated copy and validated against the source.

        Args:
            resume: Source ResumeData (immutable).
            job_analysis: Analysed job description.
            comparison: Comparison result for this resume-job pair.

        Returns:
            Validated OptimisedVariant.

        Raises:
            FabricationDetectedError: If the variant contains fabricated content.
            SchemaValidationError: If LLM response fails schema validation.
            ProviderError: If all providers fail.
        """
        variant = await self._strategy.optimise(resume, job_analysis, comparison)

        validation = validate_variant(variant, resume)
        if not validation.passed:
            logger.error(
                "resume_optimiser.fabrication_rejected",
                job_id=job_analysis.job_id,
                fabricated_items=validation.fabricated_items,
            )
            raise FabricationDetectedError(validation.fabricated_items)

        # Attach source hash for traceability
        resume_hash = _hash_resume(resume)
        variant = variant.model_copy(update={"source_resume_hash": resume_hash})

        logger.info(
            "resume_optimiser.complete",
            job_id=job_analysis.job_id,
            match_score=comparison.match_score,
            gaps=len(variant.gaps),
        )
        return variant
