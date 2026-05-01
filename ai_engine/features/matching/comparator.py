"""Comparator orchestrator — compares resume against job analysis."""

from __future__ import annotations

from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.matching.strategies.llm_comparison import LLMComparisonStrategy
from ai_engine.features.resume.models.resume_schema import ResumeData


class Comparator:
    """Orchestrates resume-job comparison.

    Args:
        strategy: LLMComparisonStrategy instance.
    """

    def __init__(self, strategy: LLMComparisonStrategy) -> None:
        self._strategy = strategy

    async def compare(self, resume: ResumeData, job_analysis: JobAnalysis) -> ComparisonResult:
        """Compare a resume against a job analysis.

        Args:
            resume: Parsed resume data.
            job_analysis: Analysed job description.

        Returns:
            ComparisonResult with match score and gap analysis.
        """
        return await self._strategy.compare(resume=resume, job_analysis=job_analysis)
