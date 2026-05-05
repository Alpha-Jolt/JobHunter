"""Session executor — manages a single pipeline session."""

from __future__ import annotations

from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import PipelineMode
from ai_engine.features.analysis.job_analyser import JobAnalyser
from ai_engine.features.matching.comparator import Comparator
from ai_engine.features.optimization.resume_optimiser import ResumeOptimiser
from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
from ai_engine.features.orchestration.models.pipeline_result import PipelineResult
from ai_engine.features.orchestration.modes.generate_mode import run_generate_mode
from ai_engine.features.output.output_builder import OutputBuilder
from ai_engine.features.resume.resume_parser import ResumeParser
from ai_engine.features.variant_management.manager import VariantManager

logger = get_logger(__name__)


class SessionExecutor:
    """Executes a single pipeline session in generate or release mode.

    Args:
        resume_parser: ResumeParser instance.
        job_analyser: JobAnalyser instance.
        comparator: Comparator instance.
        optimiser: ResumeOptimiser instance.
        variant_manager: VariantManager instance.
        output_builder: OutputBuilder instance.
    """

    def __init__(
        self,
        resume_parser: ResumeParser,
        job_analyser: JobAnalyser,
        comparator: Comparator,
        optimiser: ResumeOptimiser,
        variant_manager: VariantManager,
        output_builder: OutputBuilder,
    ) -> None:
        self._resume_parser = resume_parser
        self._job_analyser = job_analyser
        self._comparator = comparator
        self._optimiser = optimiser
        self._variant_manager = variant_manager
        self._output_builder = output_builder

    async def execute(self, config: PipelineConfig) -> PipelineResult:
        """Execute the pipeline session.

        Args:
            config: Pipeline configuration.

        Returns:
            PipelineResult with execution summary.
        """
        logger.info(
            "session_executor.start",
            session_id=config.session_id,
            mode=config.mode.value,
            user_id=config.user_id,
        )

        if config.mode == PipelineMode.GENERATE:
            result = await run_generate_mode(
                config=config,
                resume_parser=self._resume_parser,
                job_analyser=self._job_analyser,
                comparator=self._comparator,
                optimiser=self._optimiser,
                variant_manager=self._variant_manager,
            )
        else:
            # Release mode requires caller to supply variant data
            # In Phase 0, release mode is invoked directly with variant data
            result = PipelineResult(
                status="failure",
                errors=[
                    "Release mode must be invoked via run_release_mode directly with variant data."
                ],
                execution_summary="Use run_release_mode() for release operations.",
            )

        logger.info(
            "session_executor.complete",
            session_id=config.session_id,
            status=result.status,
            variants=result.generated_variants,
        )
        return result
