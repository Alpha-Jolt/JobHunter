"""Job analyser orchestrator."""

from __future__ import annotations

from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.analysis.strategies.llm_analyzer import LLMAnalyzerStrategy
from ai_engine.features.ingestion.models.job_record import JobRecord


class JobAnalyser:
    """Orchestrates job description analysis.

    Accepts a JobRecord, delegates to the LLM strategy, and returns a JobAnalysis.

    Args:
        strategy: LLMAnalyzerStrategy instance.
    """

    def __init__(self, strategy: LLMAnalyzerStrategy) -> None:
        self._strategy = strategy

    async def analyse(self, job: JobRecord) -> JobAnalysis:
        """Analyse a job record.

        If the record has a pre-computed analysis attached, it is returned directly
        without an LLM call (Phase 0+ optimisation hook).

        Args:
            job: JobRecord to analyse.

        Returns:
            JobAnalysis for the given job.
        """
        if job.pre_computed_analysis:
            return JobAnalysis(**job.pre_computed_analysis, job_id=job.job_id)

        return await self._strategy.analyse(
            job_description=job.description,
            job_id=job.job_id,
        )
