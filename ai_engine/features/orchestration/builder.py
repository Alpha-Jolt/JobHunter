"""Global Pipeline Builder for the AI Engine."""

from __future__ import annotations

from ai_engine.core.config import Settings
from ai_engine.features.analysis.job_analyser import JobAnalyser
from ai_engine.features.analysis.strategies.llm_analyzer import LLMAnalyzerStrategy
from ai_engine.features.approval.approval_gate import ApprovalGate
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.llm.router import LLMRouter
from ai_engine.features.matching.comparator import Comparator
from ai_engine.features.matching.strategies.llm_comparison import LLMComparisonStrategy
from ai_engine.features.optimization.resume_optimiser import ResumeOptimiser
from ai_engine.features.optimization.strategies.llm_optimiser_strategy import LLMOptimiserStrategy
from ai_engine.features.orchestration.executors.session_executor import SessionExecutor
from ai_engine.features.orchestration.pipeline import Pipeline
from ai_engine.features.output.output_builder import OutputBuilder
from ai_engine.features.output.strategies.llm_cover_letter_strategy import LLMCoverLetterStrategy
from ai_engine.features.resume.resume_parser import ResumeParser
from ai_engine.features.resume.strategies.llm_parser_strategy import LLMParserStrategy
from ai_engine.features.variant_management.limiters.budget_enforcer import BudgetEnforcer
from ai_engine.features.variant_management.manager import VariantManager
from shared.registries.base import VariantRegistryBase


class PipelineBuilder:
    """Builds and wires the entire AI Engine pipeline.

    Dependencies like registries are injected to keep the engine decoupled
    from PostgreSQL or specific Data Persistence Layers.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build(self, variant_registry: VariantRegistryBase) -> Pipeline:
        """Construct the full Pipeline and SessionExecutor.

        Args:
            variant_registry: An implementation of VariantRegistryBase (e.g. PostgresVariantRepository).

        Returns:
            A fully wired Pipeline instance.
        """
        router = LLMRouter(self.settings.llm)
        loader = PromptLoader(self.settings.paths.prompts_dir)
        prompt_registry = PromptRegistry(self.settings.paths.prompts_dir)

        # Build feature components with LLM strategies
        resume_parser = ResumeParser(LLMParserStrategy(router, loader, prompt_registry))
        job_analyser = JobAnalyser(LLMAnalyzerStrategy(router, loader, prompt_registry))
        comparator = Comparator(LLMComparisonStrategy(router, loader, prompt_registry))
        optimiser = ResumeOptimiser(LLMOptimiserStrategy(router, loader, prompt_registry))

        # Variant Management & Output
        budget_enforcer = BudgetEnforcer(
            max_total=self.settings.max_variants_total,
            max_per_session=self.settings.max_variants_per_session,
        )
        variant_manager = VariantManager(variant_registry, budget_enforcer)
        
        approval_gate = ApprovalGate(variant_registry)
        cover_letter_strategy = LLMCoverLetterStrategy(router, loader, prompt_registry)
        output_builder = OutputBuilder(
            approval_gate,
            cover_letter_strategy,
            self.settings.paths.output_dir,
            minio_client=None, # Will be handled by OutputBuilder internal init if None
        )

        # Orchestration
        executor = SessionExecutor(
            resume_parser=resume_parser,
            job_analyser=job_analyser,
            comparator=comparator,
            optimiser=optimiser,
            variant_manager=variant_manager,
            output_builder=output_builder,
        )

        return Pipeline(executor=executor)
