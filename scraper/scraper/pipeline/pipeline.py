"""Main pipeline orchestrator.

Stages: scrape → clean → normalize → deduplicate → output.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import List

from scraper.cleaning.cleaner_pipeline import CleanedJob, CleanerPipeline
from scraper.config import Config
from scraper.deduplication.deduplicator import Deduplicator
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.logging_.logger import Logger
from scraper.logging_.metrics import Metrics, timer
from scraper.normalization.canonical_schema import CanonicalJob
from scraper.normalization.normalizer import JobNormalizer
from scraper.output.base_output import BaseOutput
from scraper.output.csv_output import CSVOutput
from scraper.output.json_output import JSONOutput
from scraper.output.registry_output import RegistryOutput
from scraper.sources.base_scraper import BaseScraper


@dataclass
class PipelineResult:
    """Summary of a single pipeline execution."""

    source: str
    keywords: List[str]
    locations: List[str]
    raw_jobs_count: int = 0
    cleaned_jobs_count: int = 0
    normalized_jobs_count: int = 0
    final_jobs_count: int = 0
    duplicates_removed: int = 0
    errors_count: int = 0
    duration_seconds: float = 0.0
    jobs: List[CanonicalJob] = field(default_factory=list)


class ScraperPipeline:
    """Coordinates all pipeline stages for a single scraper run."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.cleaner = CleanerPipeline()
        self.normalizer = JobNormalizer()
        self.deduplicator = Deduplicator()
        self.logger = Logger.get_logger(__name__)
        self._outputs: List[BaseOutput] = self._build_outputs()

    def _build_outputs(self) -> List[BaseOutput]:
        outputs: List[BaseOutput] = []
        formats = self.config.get_output_formats()
        if "json" in formats:
            outputs.append(JSONOutput(self.config.output_dir))
        if "csv" in formats:
            outputs.append(CSVOutput(self.config.output_dir))
        if self.config.use_registry:
            from shared.registries.job_registry import JobRegistry

            outputs.append(RegistryOutput(JobRegistry(self.config.registry_path)))
        return outputs

    async def execute(
        self,
        scraper: BaseScraper,
        keywords: List[str],
        locations: List[str],
        **scraper_kwargs,
    ) -> PipelineResult:
        """Run the full pipeline and return a PipelineResult."""
        result = PipelineResult(
            source=scraper.get_source_name(),
            keywords=keywords,
            locations=locations,
        )
        start = time.monotonic()
        raw_jobs: List[IntermediateJob] = []

        try:
            with timer("pipeline_duration_seconds"):
                # Stage 1 — Scrape
                raw_jobs = await self._scrape(scraper, keywords, locations, scraper_kwargs)
                result.raw_jobs_count = len(raw_jobs)
                Metrics.counter("total_jobs_scraped").inc(len(raw_jobs))

                # Stage 2 — Clean
                cleaned_jobs = await self._clean(raw_jobs, result)
                result.cleaned_jobs_count = len(cleaned_jobs)

                # Stage 3 — Normalize
                canonical_jobs = self._normalize(cleaned_jobs, result)
                result.normalized_jobs_count = len(canonical_jobs)

                # Stage 4 — Deduplicate
                unique_jobs, dedup_report = self.deduplicator.deduplicate(canonical_jobs)
                result.final_jobs_count = len(unique_jobs)
                result.duplicates_removed = dedup_report.get("total", 0) - dedup_report.get(
                    "unique", 0
                )
                result.jobs = unique_jobs

                # Stage 5 — Output
                await self._output(unique_jobs)

        except asyncio.CancelledError:
            # Flush whatever was scraped before cancellation
            if raw_jobs:
                self.logger.warning(
                    "Pipeline cancelled — flushing partial results",
                    extra_data={"partial_raw": len(raw_jobs)},
                )
                cleaned = await self._clean(raw_jobs, result)
                canonical = self._normalize(cleaned, result)
                unique, _ = self.deduplicator.deduplicate(canonical)
                result.jobs = unique
                result.final_jobs_count = len(unique)
                await self._output(unique)
            raise

        result.duration_seconds = round(time.monotonic() - start, 2)
        self.logger.info(
            "Pipeline complete",
            extra_data={
                "source": result.source,
                "raw": result.raw_jobs_count,
                "final": result.final_jobs_count,
                "duplicates_removed": result.duplicates_removed,
                "duration_s": result.duration_seconds,
            },
        )
        return result

    async def _scrape(
        self,
        scraper: BaseScraper,
        keywords: List[str],
        locations: List[str],
        kwargs: dict,
    ) -> List[IntermediateJob]:
        try:
            return await scraper.scrape(keywords, locations, **kwargs)
        except Exception as exc:
            self.logger.error(
                "Scraping stage failed",
                extra_data={"error": str(exc)},
                exc_info=True,
            )
            Metrics.counter("errors_by_type").inc()
            return []

    async def _clean(
        self, raw_jobs: List[IntermediateJob], result: PipelineResult
    ) -> List[CleanedJob]:
        cleaned: List[CleanedJob] = []
        for job in raw_jobs:
            try:
                cleaned.append(await self.cleaner.clean(job))
            except Exception as exc:
                result.errors_count += 1
                self.logger.warning(
                    "Cleaning failed for job",
                    extra_data={"id": job.external_id, "error": str(exc)},
                )
        return cleaned

    def _normalize(
        self, cleaned_jobs: List[CleanedJob], result: PipelineResult
    ) -> List[CanonicalJob]:
        canonical: List[CanonicalJob] = []
        for job in cleaned_jobs:
            try:
                canonical.append(self.normalizer.normalize(job))
            except Exception as exc:
                result.errors_count += 1
                self.logger.warning(
                    "Normalization failed",
                    extra_data={"id": job.external_id, "error": str(exc)},
                )
        return canonical

    async def _output(self, jobs: List[CanonicalJob]) -> None:
        for output in self._outputs:
            try:
                await output.write(jobs)
            except Exception as exc:
                self.logger.error(
                    "Output write failed",
                    extra_data={"error": str(exc)},
                    exc_info=True,
                )
