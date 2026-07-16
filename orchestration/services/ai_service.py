"""AI Service — wraps AI Engine pipeline for variant generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from shared.models.exceptions import RegistryError
from shared.models.variant_record import VariantRecord
from shared.registries.base import JobRegistryBase, VariantRegistryBase

_background_tasks = set()

class AIServiceError(Exception):
    """Raised when the AI service encounters an unrecoverable error."""


class AIService:
    """Orchestrates resume variant generation using the AI Engine pipeline.

    Args:
        variant_registry: VariantRegistryBase for storing variants.
        job_registry: JobRegistryBase for fetching job records.
        master_resume_registry: Registry for master resume persistence.
        approval_service: ApprovalService for token generation.
        storage_service: StorageService for file uploads.
        ai_pipeline: AI Engine Pipeline instance.
    """

    def __init__(
        self,
        variant_registry: VariantRegistryBase,
        job_registry: JobRegistryBase,
        master_resume_registry,
        approval_service,
        storage_service,
        ai_pipeline,
    ) -> None:
        self.variant_registry = variant_registry
        self.job_registry = job_registry
        self.master_resume_registry = master_resume_registry
        self.approval_service = approval_service
        self.storage_service = storage_service
        self.ai_pipeline = ai_pipeline

    async def generate_variant(
        self,
        user_id: str,
        job_id: str,
        master_resume_path: str,
        job_record,
    ) -> VariantRecord:
        """Generate a tailored resume variant for a job.

        Args:
            user_id: User identifier.
            job_id: UUID string of the target job.
            master_resume_path: Filesystem path to the resume file.
            job_record: JobRecord from the shared DPL.

        Returns:
            VariantRecord with approval_token populated.

        Raises:
            ValueError: On invalid inputs.
            AIServiceError: On pipeline or storage failures.
        """
        # 1. Validate inputs
        if not user_id:
            raise ValueError("user_id must not be empty")
        try:
            job_uuid = uuid.UUID(str(job_id))
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"job_id is not a valid UUID: {job_id}") from exc
        resume_path = Path(master_resume_path)
        if not resume_path.exists():
            raise ValueError(f"Resume file not found: {master_resume_path}")
        if not job_record or not getattr(job_record, "description", None):
            raise ValueError("job_record must have a non-empty description")

        # Check for existing duplicate variant
        existing_variants = await self.variant_registry.get_for_job(job_uuid)
        if any(str(v.user_id) == user_id for v in existing_variants):
            raise AIServiceError("Duplicate: Variant already generated for this job")

        # 2. Parse resume and store in master_resumes
        from orchestration.core.spans import traced
        try:
            async with traced("Download Master Resume"):
                master_resume_id, parsed_json, prompt_version = (
                    await self.master_resume_registry.get_or_create(
                        user_id=user_id,
                        file_path=master_resume_path,
                    )
                )
        except Exception as exc:
            raise AIServiceError(f"Resume parsing failed: {exc}") from exc

        # 3. Build AI Engine job record from DPL job record
        try:
            from ai_engine.features.ingestion.models.job_record import (
                JobRecord as AIJobRecord,
            )

            ai_job = AIJobRecord(
                job_id=str(job_uuid),
                source=getattr(job_record, "source", "unknown"),
                title=getattr(job_record, "title", ""),
                company=getattr(job_record, "company_name", getattr(job_record, "company", "")),
                description=job_record.description,
                skills_required=list(getattr(job_record, "skills_required", [])),
                apply_email=getattr(job_record, "apply_email", "") or "",
                apply_url=getattr(job_record, "apply_url", "") or "",
                location=getattr(job_record, "location", "") or "",
            )
        except Exception as exc:
            raise AIServiceError(f"Job record conversion failed: {exc}") from exc

        # 4. Run AI pipeline (generate mode for single job)
        from orchestration.core.spans import traced
        try:
            from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
            from ai_engine.core.types import PipelineMode

            config = PipelineConfig(
                resume_file_path=resume_path,
                job_ids_to_process=[str(job_uuid)],
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                mode=PipelineMode.GENERATE,
                auto_approve=False,
            )
            # Attach the pre-ingested job to avoid filesystem reads
            config = config.model_copy(
                update={"use_shared_registry": False}
            )
            from orchestration.core.metrics import resume_generation_total, ai_request_total
            async with traced("Run AI Pipeline"):
                pipeline_result = await self._run_pipeline_for_job(
                    config=config,
                    ai_job=ai_job,
                    resume_path=resume_path,
                    user_id=user_id,
                )
            resume_generation_total.add(1)
            ai_request_total.add(1, {"provider": "anthropic"})
        except AIServiceError:
            from orchestration.core.metrics import resume_generation_failed_total, ai_failure_total
            resume_generation_failed_total.add(1)
            ai_failure_total.add(1)
            raise
        except Exception as exc:
            from orchestration.core.metrics import resume_generation_failed_total, ai_failure_total
            resume_generation_failed_total.add(1)
            ai_failure_total.add(1)
            raise AIServiceError(f"Variant generation failed: {exc}") from exc

        optimised_variant, comparison_result, variant_obj = pipeline_result

        async with traced("Persist Variant"):
            variant_id = uuid.uuid4()
            base_key = f"{user_id}/{job_uuid}"
            
            # Start async rendering if not rejected
            if variant_obj and not optimised_variant.get("is_rejected"):
                import asyncio
                task = asyncio.create_task(
                    self._render_and_upload_async(
                        variant_id, base_key, variant_obj
                    )
                )
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

            # 6. Build and store VariantRecord
            curated_json = optimised_variant.get("curated_json", {})
            gaps = optimised_variant.get("gaps", [])
            match_score = comparison_result.get("match_score", 0)

            variant_record = VariantRecord(
                variant_id=variant_id,
                user_id=user_id,
                job_id=job_uuid,
                master_resume_id=master_resume_id,
                pdf_key="",
                docx_key="",
                cover_letter_key="",
                curated_json={**curated_json, "match_score": match_score},
                gaps_identified=gaps,
                approval_status="rejected" if optimised_variant.get("is_rejected") else "pending",
                prompt_version=optimised_variant.get("prompt_version", ""),
                created_at=datetime.now(timezone.utc),
            )

            try:
                await self.variant_registry.save(variant_record)
            except RegistryError as exc:
                raise AIServiceError(str(exc)) from exc

        # 7. Generate approval token
        user_email = getattr(job_record, "apply_email", "") or ""
        token = self.approval_service.generate_approval_token(
            str(variant_id), user_email
        )
        variant_record.approval_token = token
        await self.variant_registry.update_approval_token(variant_id, token)

        return variant_record

    async def bulk_process_jobs(
        self,
        user_id: str,
        job_ids: list[str],
        master_resume_path: str,
        yield_progress=None
    ):
        """Group multiple jobs and generate one variant per group.
        
        Args:
            user_id: User identifier.
            job_ids: List of UUID strings.
            master_resume_path: Filesystem path to the resume file.
            yield_progress: Async callback function for streaming SSE progress.
        """
        import json
        from orchestration.core.spans import traced
        from ai_engine.features.llm.router import LLMRouter
        from ai_engine.core.config import get_settings as get_ai_settings
        from orchestration.db.models import Job as DBJobRecord
        
        if not job_ids:
            return

        if yield_progress: await yield_progress("Fetching job descriptions...")

        # 1. Fetch job records
        job_records: list[DBJobRecord] = []
        valid_job_ids = []
        for jid in job_ids:
            try:
                job_uuid = uuid.UUID(str(jid))
                job = await self.job_registry.get(job_uuid)
                if getattr(job, "description", None):
                    job_records.append(job)
                    valid_job_ids.append(str(job_uuid))
            except Exception:
                continue

        if not job_records:
            if yield_progress: await yield_progress("No valid jobs found to process.")
            return

        if yield_progress: await yield_progress(f"Analyzing and grouping {len(job_records)} jobs (this takes a few seconds)...")

        # 2. Group jobs via LLM
        ai_settings = get_ai_settings()
        router = LLMRouter(ai_settings.llm)
        
        jobs_json = json.dumps([
            {
                "job_id": str(job.job_id),
                "title": getattr(job, "title", ""),
                "description": getattr(job, "description", "")[:1000] # Truncate to save tokens
            } for job in job_records
        ])
        
        prompt = f"""You are an expert technical recruiter and AI assistant.
Your task is to analyze a list of job descriptions and group them into at most 3 logical role categories (e.g., "Full Stack Developer", "Data Scientist") based on similar skills and responsibilities.
For each group, synthesize a single, comprehensive "combined_description" that encapsulates the core requirements across all jobs in that group.

Jobs:
{jobs_json}

Return a JSON object containing an array of groups, each with a 'role_name', a list of 'job_ids' belonging to it, and the 'combined_description'. Each job_id MUST be assigned to exactly one group.
"""
        schema = {
            "type": "object",
            "properties": {
                "groups": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role_name": {"type": "string"},
                            "job_ids": {"type": "array", "items": {"type": "string"}},
                            "combined_description": {"type": "string"}
                        },
                        "required": ["role_name", "job_ids", "combined_description"]
                    }
                }
            },
            "required": ["groups"]
        }
        
        try:
            llm_result = await router.complete(prompt, schema, "bulk_grouper_v1")
            group_data = json.loads(llm_result.content)
            groups = group_data.get("groups", [])
        except Exception as e:
            if yield_progress: await yield_progress(f"Failed to group jobs: {e}. Falling back to individual processing.")
            groups = [{"role_name": "Fallback", "job_ids": valid_job_ids, "combined_description": getattr(job_records[0], "description", "")}]

        if yield_progress: await yield_progress(f"Jobs categorized into {len(groups)} distinct roles. Generating variants...")

        # 3. Process each group
        from ai_engine.features.ingestion.models.job_record import JobRecord as AIJobRecord
        from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
        from ai_engine.core.types import PipelineMode

        for idx, group in enumerate(groups):
            g_job_ids = group.get("job_ids", [])
            # Filter to only job_ids we actually fetched
            g_job_ids = [j for j in g_job_ids if j in valid_job_ids]
            if not g_job_ids:
                continue
                
            role_name = group.get("role_name", "Unknown Role")
            if yield_progress: await yield_progress(f"Generating optimized resume for: {role_name} ({len(g_job_ids)} jobs) - Group {idx+1}/{len(groups)}...")
            
            # Create a pseudo job for the group
            pseudo_job = AIJobRecord(
                job_id=g_job_ids[0], # Just use the first one as a dummy ID for the pipeline
                source="bulk_grouping",
                title=role_name,
                company="Multiple Companies",
                description=group.get("combined_description", ""),
                skills_required=[],
                apply_email="",
                apply_url="",
                location="Various",
            )
            
            config = PipelineConfig(
                resume_file_path=Path(master_resume_path),
                job_ids_to_process=[g_job_ids[0]],
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                mode=PipelineMode.GENERATE,
                auto_approve=False,
                use_shared_registry=False,
            )
            
            try:
                pipeline_result = await self._run_pipeline_for_job(
                    config=config,
                    ai_job=pseudo_job,
                    resume_path=Path(master_resume_path),
                    user_id=user_id,
                )
            except Exception as e:
                if yield_progress: await yield_progress(f"Warning: Failed to generate variant for {role_name}: {e}")
                continue
                
            optimised_variant, comparison_result, variant_obj = pipeline_result

            # 4. Save ONE VariantRecord per role group (not per job_id).
            #    The representative job is the first in the group; all grouped
            #    job_ids are stored in curated_json for traceability.
            master_resume_id, _, _ = await self.master_resume_registry.get_or_create(
                user_id=user_id, file_path=master_resume_path
            )

            representative_job_id = uuid.UUID(g_job_ids[0])
            variant_id = uuid.uuid4()
            base_key = f"{user_id}/{representative_job_id}"

            curated_json = optimised_variant.get("curated_json", {})
            gaps = optimised_variant.get("gaps", [])
            match_score = comparison_result.get("match_score", 0)

            variant_record = VariantRecord(
                variant_id=variant_id,
                user_id=user_id,
                job_id=representative_job_id,
                master_resume_id=master_resume_id,
                pdf_key="",
                docx_key="",
                cover_letter_key="",
                curated_json={
                    **curated_json,
                    "match_score": match_score,
                    "role_name": role_name,
                    "grouped_job_ids": g_job_ids,  # All jobs this variant covers
                },
                gaps_identified=gaps,
                approval_status="rejected" if optimised_variant.get("is_rejected") else "pending",
                prompt_version=optimised_variant.get("prompt_version", ""),
                created_at=datetime.now(timezone.utc),
            )

            await self.variant_registry.save(variant_record)

            # Background render/upload
            if variant_obj and not optimised_variant.get("is_rejected"):
                import asyncio
                task = asyncio.create_task(
                    self._render_and_upload_async(variant_id, base_key, variant_obj)
                )
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

            # Approval token — use representative job's apply_email
            original_job = next((j for j in job_records if str(j.job_id) == g_job_ids[0]), None)
            user_email = getattr(original_job, "apply_email", "") or "" if original_job else ""
            token = self.approval_service.generate_approval_token(str(variant_id), user_email)
            variant_record.approval_token = token
            await self.variant_registry.update_approval_token(variant_id, token)

            if yield_progress:
                await yield_progress(
                    f"Variant saved for '{role_name}' covering {len(g_job_ids)} job(s)."
                )

    async def _render_and_upload_async(self, variant_id, base_key, variant_obj):
        """Background task: render DOCX/PDF and upload to MinIO, then UPDATE the DB row.

        Fixes:
        - Uses str(variant_id) in WHERE clause to match the VARCHAR column (UUID mismatch fix).
        - Marks s3_upload_failed=True and stores local_pdf_path when MinIO upload fails.
        - Logs storage errors at ERROR level so they are visible in monitoring.
        """
        import tempfile
        from pathlib import Path
        from ai_engine.features.output.renderers.resume_renderer import render_resume
        from ai_engine.core.logging_.logger import get_logger
        from orchestration.db.connection import get_session_factory
        import orchestration.db.models as _m
        from sqlalchemy import update

        logger = get_logger(__name__)
        temp_dir = tempfile.mkdtemp()
        # Use str(variant_id) — DB column is VARCHAR, not native UUID.
        variant_id_str = str(variant_id)

        try:
            out_dir = Path(temp_dir)
            docx_path_str, pdf_path_str = await render_resume(variant_obj, out_dir)

            # --- Upload to MinIO ---
            storage_failed = False
            docx_key = ""
            pdf_key = ""
            local_pdf_path = pdf_path_str or ""

            try:
                docx_key = await self.storage_service.upload_file(
                    docx_path_str,
                    f"variants/{base_key}/resume.docx",
                )
                if pdf_path_str and Path(pdf_path_str).exists():
                    pdf_key = await self.storage_service.upload_file(
                        pdf_path_str,
                        f"variants/{base_key}/resume.pdf",
                    )
            except Exception as upload_exc:
                # MinIO is unreachable or misconfigured. Mark the variant so the
                # frontend can surface a recoverable error instead of showing nothing.
                storage_failed = True
                logger.error(
                    "minio_upload_failed",
                    variant_id=variant_id_str,
                    base_key=base_key,
                    error=str(upload_exc),
                )

            # --- UPDATE the DB row in a new independent session ---
            async_session_maker = get_session_factory()
            async with async_session_maker() as session:
                update_values: dict = {
                    "docx_key": docx_key,
                    "pdf_key": pdf_key,
                    "s3_upload_failed": storage_failed,
                    "local_pdf_path": local_pdf_path if storage_failed else "",
                }
                result = await session.execute(
                    update(_m.ResumeVariant)
                    .where(_m.ResumeVariant.variant_id == variant_id_str)
                    .values(**update_values)
                )
                await session.commit()
                if result.rowcount == 0:
                    logger.error(
                        "render_upload_update_missed",
                        variant_id=variant_id_str,
                        detail="UPDATE matched 0 rows",
                    )
        except Exception as exc:
            logger.error("async_render_failed", variant_id=variant_id_str, error=str(exc))
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def _run_pipeline_for_job(
        self,
        config,
        ai_job,
        resume_path: Path,
        user_id: str,
    ) -> tuple:
        """Run AI Engine components directly for a single job.

        Returns:
            Tuple of (optimised_variant_dict, comparison_result_dict).
        """
        import time
        from orchestration.core.metrics import ai_request_duration, resume_processing_duration
        
        start_time = time.perf_counter()
        
        if not self.ai_pipeline:
            raise AIServiceError("AI Pipeline is not initialized.")
            
        executor = self.ai_pipeline._executor

        try:
            resume = await executor._resume_parser.parse(resume_path)
        except Exception as exc:
            raise AIServiceError(f"Resume parsing failed: {exc}") from exc

        try:
            analysis = await executor._job_analyser.analyse(ai_job)
        except Exception as exc:
            raise AIServiceError(f"Job analysis failed: {exc}") from exc

        try:
            comparison = await executor._comparator.compare(resume, analysis)
            if comparison.match_score < 45:
                variant = None
            else:
                variant = await executor._optimiser.optimise(resume, analysis, comparison)
        except Exception as exc:
            raise AIServiceError(f"Variant generation failed: {exc}") from exc
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            ai_request_duration.record(duration_ms)
            resume_processing_duration.record(duration_ms)

        if variant:
            curated_json = {
                "personal": resume.personal.model_dump(),
                "summary": variant.rewritten_summary,
                "experience": [e.model_dump() for e in variant.reordered_experience],
                "skills": variant.prioritized_skills,
                "projects": [p.model_dump() for p in variant.selected_projects],
                "certifications": variant.selected_certifications,
            }
            gaps = list(variant.gaps)
            prompt_version = variant.prompt_version_used
        else:
            curated_json = {
                "personal": resume.personal.model_dump(),
                "summary": "Rejected: Match score too low.",
                "experience": [],
                "skills": comparison.matched_skills,
                "projects": [],
                "certifications": [],
            }
            gaps = comparison.gap_skills
            prompt_version = comparison.prompt_version_used

        return (
            {
                "curated_json": curated_json,
                "gaps": gaps,
                "prompt_version": prompt_version,
                "match_score": comparison.match_score,
                "pdf_path": "",
                "docx_path": "",
                "cover_letter_path": "",
                "is_rejected": variant is None,
            },
            {
                "match_score": comparison.match_score,
            },
            variant
        )

    async def get_pending_variants(self, user_id: uuid.UUID) -> List[VariantRecord]:
        """Return all pending variants for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of pending VariantRecord instances.
        """
        return await self.variant_registry.get_pending_for_user(user_id)

    async def get_variant_details(self, variant_id: str) -> dict:
        """Return full details for a variant.

        Args:
            variant_id: UUID string of the variant.

        Returns:
            Dict with curated_resume, gaps, match_score, etc.

        Raises:
            VariantNotFoundError: If variant does not exist.
            AIServiceError: If data parsing fails.
        """
        try:
            vid = uuid.UUID(variant_id)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Invalid variant_id: {variant_id}") from exc

        record = await self.variant_registry.get(vid)

        try:
            curated = dict(record.curated_json or {})
            match_score = curated.pop("match_score", 0)
        except Exception as exc:
            raise AIServiceError(f"Failed to parse variant data: {exc}") from exc

        return {
            "variant_id": str(record.variant_id),
            "job_id": str(record.job_id),
            "user_id": record.user_id,
            "curated_resume": curated,
            "gaps": list(record.gaps_identified or []),
            "approval_status": record.approval_status,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "match_score": match_score,
        }
