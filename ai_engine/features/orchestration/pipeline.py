"""Main pipeline orchestrator."""

from __future__ import annotations

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.orchestration.executors.session_executor import SessionExecutor
from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
from ai_engine.features.orchestration.models.pipeline_result import PipelineResult

logger = get_logger(__name__)


class Pipeline:
    """Top-level pipeline orchestrator.

    Accepts a PipelineConfig, creates a session, and delegates execution.

    Args:
        executor: SessionExecutor instance.
    """

    def __init__(self, executor: SessionExecutor) -> None:
        self._executor = executor

    async def run(self, config: PipelineConfig) -> PipelineResult:
        """Run the pipeline with the given configuration.

        Args:
            config: Pipeline execution configuration.

        Returns:
            PipelineResult with final execution summary.
        """
        logger.info("pipeline.start", session_id=config.session_id, mode=config.mode.value)
        result = await self._executor.execute(config)
        logger.info("pipeline.complete", status=result.status, session_id=config.session_id)
        return result
