"""AI Engine API routes — /api/ai/*"""

from __future__ import annotations

import uuid
from typing import Optional
import os
import shutil
import tempfile
import asyncio
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from orchestration.auth.dependencies import get_current_user, require_role
from orchestration.auth.models.user import RoleEnum, UserRecord
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.config import get_settings
from orchestration.api.dependencies import get_db_session, get_external_s3_client
from orchestration.repositories.postgres_job_repository import PostgresJobRepository
from orchestration.repositories.postgres_master_resume_repository import (
    PostgresMasterResumeRepository,
)
from orchestration.repositories.postgres_variant_repository import PostgresVariantRepository
from orchestration.services.ai_service import AIService, AIServiceError
from orchestration.services.approval_service import (
    ApprovalService,
    TokenAlreadyUsedError,
    TokenExpiredError,
    TokenInvalidError,
)
from orchestration.services.storage_service import StorageService
from shared.models.exceptions import JobNotFoundError, RegistryError, VariantNotFoundError

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_approval_link(request_base: str, variant_id: str, token: str) -> str:
    return f"{request_base}/api/ai/approve/{variant_id}?token={token}"


def _get_approval_service(session: AsyncSession) -> ApprovalService:
    settings = get_settings()
    variant_repo = PostgresVariantRepository(session)
    return ApprovalService(
        variant_registry=variant_repo,
        secret_key=settings.api.approval_token_secret,
    )


def _get_ai_service(session: AsyncSession) -> AIService:
    settings = get_settings()
    variant_repo = PostgresVariantRepository(session)
    job_repo = PostgresJobRepository(session)
    master_resume_repo = PostgresMasterResumeRepository(session)
    approval_svc = ApprovalService(
        variant_registry=variant_repo,
        secret_key=settings.api.approval_token_secret,
    )
    import boto3
    from botocore.config import Config
    scheme = "https" if settings.minio.minio_secure else "http"
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"{scheme}://{settings.minio.minio_endpoint}",
        aws_access_key_id=settings.minio.minio_access_key,
        aws_secret_access_key=settings.minio.minio_secret_key,
        config=Config(signature_version="s3v4"),
    )
    storage_svc = StorageService(
        output_dir=settings.paths.ai_resume_dir,
        s3_client=s3_client,
        bucket_name=settings.minio.minio_bucket,
    )

    from ai_engine.core.config import get_settings as get_ai_settings
    from ai_engine.features.orchestration.builder import PipelineBuilder

    ai_settings = get_ai_settings()
    builder = PipelineBuilder(ai_settings)
    ai_pipeline = builder.build(variant_registry=variant_repo)

    # ai_pipeline is None in Phase 0 — generate_variant handles it
    return AIService(
        variant_registry=variant_repo,
        job_registry=job_repo,
        master_resume_registry=master_resume_repo,
        approval_service=approval_svc,
        storage_service=storage_svc,
        ai_pipeline=ai_pipeline,
    )


# ── Request / Response schemas ────────────────────────────────────────────────

class GenerateVariantRequest(BaseModel):
    user_id: str
    job_id: str
    resume_file_path: str


class BulkGenerateVariantRequest(BaseModel):
    user_id: str
    job_ids: list[str]
    resume_file_path: str


class GenerateVariantResponse(BaseModel):
    variant_id: str
    approval_token: str
    job_title: str
    company_name: str
    match_score: float
    created_at: Optional[str]
    status: str
    approval_link: str


class VariantSummary(BaseModel):
    variant_id: str
    job_id: str
    job_title: str
    company_name: str
    match_score: float
    created_at: Optional[str]
    approval_link: str


class PendingVariantsResponse(BaseModel):
    total: int
    pending: list[VariantSummary]


class VariantSummaryFull(BaseModel):
    variant_id: str
    job_id: str
    job_title: str
    company_name: str
    match_score: float
    approval_status: str
    created_at: Optional[str]
    approved_at: Optional[str]
    approval_link: str
    pdf_key: str
    docx_key: str
    s3_upload_failed: bool


class AllVariantsResponse(BaseModel):
    total: int
    variants: list[VariantSummaryFull]


class PreviewVariantResponse(BaseModel):
    variant_id: str
    approval_status: str
    curated_resume: dict
    gaps: list[str]
    match_score: float


class ApproveVariantRequest(BaseModel):
    approval_token: Optional[str] = None


class ApproveVariantResponse(BaseModel):
    variant_id: str
    status: str
    approved_at: Optional[str]
    message: str


class RejectVariantRequest(BaseModel):
    user_feedback: Optional[str] = None


class RejectVariantResponse(BaseModel):
    variant_id: str
    status: str
    message: str
    feedback_stored: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/jobs/raw",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(RoleEnum.ADMIN, RoleEnum.HUNTER))]
)
async def get_raw_jobs(
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch raw jobs for the AI engine to process."""
    job_repo = PostgresJobRepository(session)
    jobs = await job_repo.get_by_status("raw")
    return {"jobs": jobs}

@router.post("/generate", response_model=GenerateVariantResponse, status_code=status.HTTP_200_OK)
async def generate_variant(
    body: GenerateVariantRequest,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> GenerateVariantResponse:
    """Generate a tailored resume variant for a job."""
    # Ownership: user_id in body must match the authenticated user.
    # Admins may generate on behalf of any user.
    if current_user.role != "admin" and body.user_id != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot generate variant for another user.")

    # Resume ownership: S3 key must be scoped to the requesting user.
    expected_prefix = f"resumes/{body.user_id}/"
    if not body.resume_file_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=403,
            detail="Resume file does not belong to the specified user.",
        )

    ai_service = _get_ai_service(session)
    job_repo = PostgresJobRepository(session)

    # Fetch job
    try:
        job_uuid = uuid.UUID(body.job_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Invalid job_id: {body.job_id}")

    try:
        job_record = await job_repo.get(job_uuid)
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job not found: {body.job_id}")

    # Download resume from MinIO
    settings = get_settings()
    scheme = "https" if settings.minio.minio_secure else "http"
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"{scheme}://{settings.minio.minio_endpoint}",
        aws_access_key_id=settings.minio.minio_access_key,
        aws_secret_access_key=settings.minio.minio_secret_key,
        region_name="us-east-1",
    )
    bucket_name = settings.minio.minio_bucket
    s3_key = body.resume_file_path

    # Preserve filename for the master_resume_registry
    file_name = Path(s3_key).name
    temp_dir = tempfile.mkdtemp(dir=os.getcwd())
    local_resume_path = os.path.join(temp_dir, file_name)

    def _download_from_minio():
        s3_client.download_file(bucket_name, s3_key, local_resume_path)

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download_from_minio)
    except ClientError as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=404, detail=f"Resume file not found in storage: {exc}")

    try:
        variant = await ai_service.generate_variant(
            user_id=body.user_id,
            job_id=body.job_id,
            master_resume_path=local_resume_path,
            job_record=job_record,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AIServiceError as exc:
        msg = str(exc)
        if "already exists" in msg.lower() or "duplicate" in msg.lower():
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=500, detail=msg)
    except RegistryError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    curated = dict(variant.curated_json or {})
    match_score = float(curated.pop("match_score", 0))
    token = variant.approval_token or ""
    base_url = "http://localhost:8000"

    return GenerateVariantResponse(
        variant_id=str(variant.variant_id),
        approval_token=token,
        job_title=getattr(job_record, "title", ""),
        company_name=getattr(job_record, "company_name", ""),
        match_score=match_score,
        created_at=variant.created_at.isoformat() if variant.created_at else None,
        status=variant.approval_status,
        approval_link=_make_approval_link(base_url, str(variant.variant_id), token),
    )


@router.post("/bulk-generate", status_code=status.HTTP_200_OK)
async def bulk_generate_variants(
    body: BulkGenerateVariantRequest,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Generate tailored resume variants for multiple jobs using SSE for progress."""
    # Ownership checks
    if current_user.role != "admin" and body.user_id != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot generate variants for another user.")

    expected_prefix = f"resumes/{body.user_id}/"
    if not body.resume_file_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=403,
            detail="Resume file does not belong to the specified user.",
        )

    if not body.job_ids:
        raise HTTPException(status_code=400, detail="job_ids cannot be empty")
    
    if len(body.job_ids) > 100:
        raise HTTPException(status_code=400, detail="Cannot process more than 100 jobs at a time")

    # Use a Queue to stream SSE events from the background task
    queue = asyncio.Queue()

    async def yield_progress(message: str):
        await queue.put(f"data: {{\"status\": \"Processing\", \"message\": \"{message}\"}}\n\n")

    async def run_bulk():
        # IMPORTANT: This runs as a detached background task after the route's
        # session dependency has been torn down. Must open its own session.
        from orchestration.db.connection import get_session_factory
        temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        try:
            async_session_maker = get_session_factory()
            async with async_session_maker() as bulk_session:
                ai_service = _get_ai_service(bulk_session)

                settings = get_settings()
                scheme = "https" if settings.minio.minio_secure else "http"
                s3_client = boto3.client(
                    "s3",
                    endpoint_url=f"{scheme}://{settings.minio.minio_endpoint}",
                    aws_access_key_id=settings.minio.minio_access_key,
                    aws_secret_access_key=settings.minio.minio_secret_key,
                    region_name="us-east-1",
                )
                bucket_name = settings.minio.minio_bucket
                s3_key = body.resume_file_path

                file_name = Path(s3_key).name
                local_resume_path = os.path.join(temp_dir, file_name)

                def _download_from_minio():
                    s3_client.download_file(bucket_name, s3_key, local_resume_path)

                await asyncio.get_event_loop().run_in_executor(None, _download_from_minio)

                await ai_service.bulk_process_jobs(
                    user_id=body.user_id,
                    job_ids=body.job_ids,
                    master_resume_path=local_resume_path,
                    yield_progress=yield_progress,
                )
                await bulk_session.commit()

            await queue.put("data: {\"status\": \"Success\", \"message\": \"Bulk variant generation completed.\"}\n\n")
        except Exception as e:
            import traceback
            traceback.print_exc()
            await queue.put(f'data: {{"status": "Error", "message": "Error: {str(e)}"}}' + "\n\n")
        finally:
            await queue.put(None)  # Signal end of stream
            shutil.rmtree(temp_dir, ignore_errors=True)

    # Start the background task
    asyncio.create_task(run_bulk())

    async def event_generator():
        yield "data: {\"status\": \"Queued\", \"message\": \"Batch queued for processing\"}\n\n"
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get(
    "/pending/{user_id}",
    response_model=PendingVariantsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_pending_variants(
    user_id: str,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PendingVariantsResponse:
    """List all pending variants awaiting approval for a user."""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id must not be empty")

    # Ownership: hunters may only query their own variants.
    if current_user.role != "admin" and user_id != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot access another user's variants.")

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    ai_service = _get_ai_service(session)
    job_repo = PostgresJobRepository(session)
    variants = await ai_service.get_pending_variants(user_uuid)

    base_url = "http://localhost:8000"
    summaries = []
    for v in variants:
        curated = dict(v.curated_json or {})
        match_score = float(curated.get("match_score", 0))
        job_title = ""
        company_name = ""
        try:
            job = await job_repo.get(v.job_id)
            job_title = getattr(job, "title", "")
            company_name = getattr(job, "company_name", "")
        except Exception:
            pass

        summaries.append(
            VariantSummary(
                variant_id=str(v.variant_id),
                job_id=str(v.job_id),
                job_title=job_title,
                company_name=company_name,
                match_score=match_score,
                created_at=v.created_at.isoformat() if v.created_at else None,
                approval_link=_make_approval_link(
                    base_url, str(v.variant_id), v.approval_token or ""
                ),
            )
        )

    return PendingVariantsResponse(total=len(summaries), pending=summaries)


@router.get(
    "/variants/{user_id}",
    response_model=AllVariantsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_variants(
    user_id: str,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AllVariantsResponse:
    """List all variants for a user across all statuses (pending/approved/rejected).

    Approved variants remain visible with approval_status='approved' so users
    can review, download, or track their history.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id must not be empty")

    # Ownership: hunters may only access their own variants.
    if current_user.role != "admin" and user_id != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot access another user's variants.")

    variant_repo = PostgresVariantRepository(session)
    job_repo = PostgresJobRepository(session)
    variants = await variant_repo.get_for_user(user_id)

    base_url = "http://localhost:8000"
    summaries = []
    for v in variants:
        curated = dict(v.curated_json or {})
        match_score = float(curated.get("match_score", 0))
        job_title = ""
        company_name = ""
        try:
            job = await job_repo.get(v.job_id)
            job_title = getattr(job, "title", "")
            company_name = getattr(job, "company_name", "")
        except Exception:
            pass

        summaries.append(
            VariantSummaryFull(
                variant_id=str(v.variant_id),
                job_id=str(v.job_id),
                job_title=job_title,
                company_name=company_name,
                match_score=match_score,
                approval_status=v.approval_status,
                created_at=v.created_at.isoformat() if v.created_at else None,
                approved_at=v.approved_at.isoformat() if v.approved_at else None,
                approval_link=_make_approval_link(
                    base_url, str(v.variant_id), v.approval_token or ""
                ),
                pdf_key=v.pdf_key or "",
                docx_key=v.docx_key or "",
                s3_upload_failed=bool(v.s3_upload_failed),
            )
        )

    # Sort: pending first, then approved, then rejected — newest first within each group
    order = {"pending": 0, "approved": 1, "rejected": 2}
    summaries.sort(key=lambda x: (order.get(x.approval_status, 9), x.created_at or ""), reverse=False)

    return AllVariantsResponse(total=len(summaries), variants=summaries)


@router.get(
    "/preview/{variant_id}",
    response_model=PreviewVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_variant(
    variant_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> PreviewVariantResponse:
    """Preview the curated resume content before approving."""
    try:
        uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Invalid variant_id: {variant_id}")

    ai_service = _get_ai_service(session)
    try:
        details = await ai_service.get_variant_details(variant_id)
    except VariantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Variant not found: {variant_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return PreviewVariantResponse(
        variant_id=details["variant_id"],
        approval_status=details["approval_status"],
        curated_resume=details["curated_resume"],
        gaps=details["gaps"],
        match_score=float(details.get("match_score", 0)),
    )


@router.get(
    "/download/{variant_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def download_variant(
    variant_id: str,
    format: str = Query(default="docx"),
    session: AsyncSession = Depends(get_db_session),
    s3_client = Depends(get_external_s3_client),
):
    """Download the generated resume variant (docx or pdf)."""
    try:
        vid = uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid variant_id")

    variant_repo = PostgresVariantRepository(session)
    try:
        variant = await variant_repo.get(vid)
    except Exception:
        raise HTTPException(status_code=404, detail="Variant not found")

    settings = get_settings()
    
    file_key = variant.docx_key if format == "docx" else variant.pdf_key
    if not file_key:
        raise HTTPException(status_code=404, detail=f"No {format} file generated for this variant yet")

    from fastapi.responses import RedirectResponse
    
    filename = f"Resume_{variant_id}.{format}"
    # Force download via response-content-disposition
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.minio.minio_bucket, 
            'Key': file_key,
            'ResponseContentDisposition': f'attachment; filename="{filename}"'
        },
        ExpiresIn=3600
    )
    return RedirectResponse(url=url)


@router.get(
    "/pdf-preview/{variant_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def pdf_preview(
    variant_id: str,
    session: AsyncSession = Depends(get_db_session),
    s3_client=Depends(get_external_s3_client),
):
    """Return a presigned URL for inline PDF preview (opens in browser, not download)."""
    try:
        vid = uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid variant_id")

    variant_repo = PostgresVariantRepository(session)
    try:
        variant = await variant_repo.get(vid)
    except Exception:
        raise HTTPException(status_code=404, detail="Variant not found")

    settings = get_settings()
    file_key = variant.pdf_key
    if not file_key:
        # Fall back to docx if pdf not generated
        raise HTTPException(
            status_code=404,
            detail="PDF not yet generated for this variant. Try again shortly or download the DOCX.",
        )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.minio.minio_bucket,
            "Key": file_key,
            "ResponseContentType": "application/pdf",
            "ResponseContentDisposition": "inline",
        },
        ExpiresIn=3600,
    )
    return {"url": url, "variant_id": variant_id, "expires_in": 3600}


@router.get(
    "/variant/{variant_id}/token",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def get_variant_approval_token(
    variant_id: str,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Return the approval token for a variant the authenticated user owns."""
    try:
        variant_uuid = uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid variant_id")

    from orchestration.repositories.postgres_variant_repository import PostgresVariantRepository
    variant_repo = PostgresVariantRepository(session)
    try:
        variant = await variant_repo.get(variant_uuid)
    except Exception:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Ownership check — user can only fetch their own variant's token
    if str(variant.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not variant.approval_token:
        raise HTTPException(status_code=404, detail="Approval token not found")

    return {"approval_token": variant.approval_token}


@router.post(
    "/approve/{variant_id}",
    response_model=ApproveVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_variant(
    variant_id: str,
    token: Optional[str] = Query(default=None),
    body: ApproveVariantRequest = ApproveVariantRequest(),
    session: AsyncSession = Depends(get_db_session),
) -> ApproveVariantResponse:
    """Approve a variant via signed token."""
    approval_token = token or (body.approval_token if body else None)
    if not approval_token:
        raise HTTPException(status_code=400, detail="approval_token is required")

    try:
        uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Invalid variant_id: {variant_id}")

    approval_svc = _get_approval_service(session)

    try:
        recovered_id = approval_svc.validate_approval_token(approval_token)
    except TokenInvalidError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid token: {exc}")
    except TokenExpiredError as exc:
        raise HTTPException(status_code=401, detail=f"Token expired: {exc}")

    if recovered_id != variant_id:
        raise HTTPException(status_code=400, detail="Token does not match variant_id")

    try:
        updated = await approval_svc.mark_approved(variant_id)
    except TokenAlreadyUsedError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except VariantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Variant not found: {variant_id}")

    return ApproveVariantResponse(
        variant_id=variant_id,
        status="approved",
        approved_at=updated.approved_at.isoformat() if updated.approved_at else None,
        message="Variant approved. Ready to send application.",
    )


@router.post(
    "/reject/{variant_id}",
    response_model=RejectVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def reject_variant(
    variant_id: str,
    body: RejectVariantRequest = RejectVariantRequest(),
    session: AsyncSession = Depends(get_db_session),
) -> RejectVariantResponse:
    """Reject a pending variant and optionally store user feedback."""
    try:
        vid = uuid.UUID(variant_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Invalid variant_id: {variant_id}")

    variant_repo = PostgresVariantRepository(session)

    try:
        record = await variant_repo.get(vid)
    except VariantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Variant not found: {variant_id}")

    if record.approval_status == "approved":
        raise HTTPException(status_code=409, detail="Cannot reject an already approved variant")

    await variant_repo.update_approval_status(vid, "rejected")

    # Store feedback if provided
    feedback_stored = False
    if body and body.user_feedback:
        from sqlalchemy import update
        import orchestration.db.models as _m
        await session.execute(
            update(_m.ResumeVariant)
            .where(_m.ResumeVariant.variant_id == str(vid))
            .values(user_feedback=body.user_feedback)
        )
        feedback_stored = True

    return RejectVariantResponse(
        variant_id=variant_id,
        status="rejected",
        message="Variant rejected. You can generate a new variant if needed.",
        feedback_stored=feedback_stored,
    )
