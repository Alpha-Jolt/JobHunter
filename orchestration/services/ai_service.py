"""AI Service — wraps AI Engine pipeline for variant generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from shared.models.exceptions import RegistryError
from shared.models.variant_record import VariantRecord
from shared.registries.base import JobRegistryBase, VariantRegistryBase


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

        # 2. Parse resume and store in master_resumes
        try:
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
            pipeline_result = await self._run_pipeline_for_job(
                config=config,
                ai_job=ai_job,
                resume_path=resume_path,
                user_id=user_id,
            )
        except AIServiceError:
            raise
        except Exception as exc:
            raise AIServiceError(f"Variant generation failed: {exc}") from exc

        optimised_variant, comparison_result = pipeline_result

        # 5. Upload output files to storage
        variant_id = uuid.uuid4()
        base_key = f"{user_id}/{job_uuid}"
        try:
            pdf_key = await self.storage_service.upload_file(
                optimised_variant.get("pdf_path", ""),
                f"{base_key}/resume.pdf",
            )
            docx_key = await self.storage_service.upload_file(
                optimised_variant.get("docx_path", ""),
                f"{base_key}/resume.docx",
            )
            cover_letter_key = await self.storage_service.upload_file(
                optimised_variant.get("cover_letter_path", ""),
                f"{base_key}/cover_letter.pdf",
            )
        except Exception as exc:
            raise AIServiceError(f"File storage failed: {exc}") from exc

        # 6. Build and store VariantRecord
        curated_json = optimised_variant.get("curated_json", {})
        gaps = optimised_variant.get("gaps", [])
        match_score = comparison_result.get("match_score", 0)

        variant_record = VariantRecord(
            variant_id=variant_id,
            user_id=user_id,
            job_id=job_uuid,
            master_resume_id=master_resume_id,
            pdf_key=pdf_key,
            docx_key=docx_key,
            cover_letter_key=cover_letter_key,
            curated_json={**curated_json, "match_score": match_score},
            gaps_identified=gaps,
            approval_status="pending",
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
            variant = await executor._optimiser.optimise(resume, analysis, comparison)
        except Exception as exc:
            raise AIServiceError(f"Variant generation failed: {exc}") from exc

        curated_json = {
            "personal": resume.personal.model_dump(),
            "summary": variant.rewritten_summary,
            "experience": [e.model_dump() for e in variant.reordered_experience],
            "skills": variant.prioritized_skills,
            "projects": [p.model_dump() for p in variant.selected_projects],
            "certifications": variant.selected_certifications,
        }

        return (
            {
                "curated_json": curated_json,
                "gaps": list(variant.gaps),
                "prompt_version": variant.prompt_version_used,
                "match_score": comparison.match_score,
                "pdf_path": "",
                "docx_path": "",
                "cover_letter_path": "",
            },
            {
                "match_score": comparison.match_score,
            },
        )

    async def get_pending_variants(self, user_id: str) -> List[VariantRecord]:
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
