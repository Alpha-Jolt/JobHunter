"""Resume upload endpoint — POST /api/resume/upload"""

from __future__ import annotations

import asyncio
import re
import tempfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis
import uuid
from datetime import datetime, timezone

from orchestration.api.config import get_settings
from orchestration.api.dependencies import get_db_session, get_internal_s3_client, get_external_s3_client
from orchestration.auth.dependencies import get_current_user, require_role
from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.db.models import MasterResume

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB

# Magic byte signatures
MAGIC_BYTES: dict[str, bytes] = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
}

# Malicious PDF patterns — CVE-known vectors
_PDF_MALICIOUS_PATTERNS = [
    b"/JavaScript",
    b"/JS ",
    b"/OpenAction",
    b"/Launch",
    b"/EmbeddedFile",
    b"/AA ",          # Additional Actions
    b"/RichMedia",
    b"eval(",
]

# Filename sanitizer: allow only safe characters
_SAFE_FILENAME = re.compile(r"^[a-zA-Z0-9_\-. ]{1,200}$")


def _sanitize_filename(name: str) -> str:
    """Strip path components and validate character set."""
    name = Path(name).name  # drop any directory prefix
    name = name.replace("\x00", "")  # strip null bytes
    if not _SAFE_FILENAME.match(name):
        # Replace unsafe chars with underscore
        name = re.sub(r"[^a-zA-Z0-9_\-. ]", "_", name)
    return name


def _validate_magic(ext: str, header: bytes) -> bool:
    expected = MAGIC_BYTES.get(ext)
    if not expected:
        return False
    return header[: len(expected)] == expected


def _scan_pdf_threats(content: bytes) -> str | None:
    """Return a description if a known malicious pattern is found."""
    sample = content[:65536]  # scan first 64 KB
    for pattern in _PDF_MALICIOUS_PATTERNS:
        if pattern in sample:
            return f"Unsafe pattern detected: {pattern.decode(errors='replace')}"
    return None


def _scan_docx_threats(content: bytes) -> str | None:
    """
    DOCX is a ZIP. Reject if it contains macros (vbaProject.bin)
    or external relationships that could execute code.
    """
    import zipfile
    import io

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = zf.namelist()
            for name in names:
                lower = name.lower()
                if "vbaproject.bin" in lower:
                    return "Document contains VBA macros and cannot be uploaded."
                if "externallinks" in lower:
                    return "Document contains external links and cannot be uploaded."
    except zipfile.BadZipFile:
        return "File is not a valid DOCX archive."
    return None


class ResumeUploadResponse(BaseModel):
    s3_key: str
    file_name: str


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    current_user: UserRecord = Depends(get_current_user),
    _session: AsyncSession = Depends(get_db_session),
    s3_client = Depends(get_internal_s3_client),
) -> ResumeUploadResponse:
    """Upload a master resume (PDF or DOCX) to MinIO.

    Security checks applied in order:
    1. Extension whitelist (.pdf, .docx only)
    2. Content-Type whitelist
    3. File size cap (10 MB)
    4. Magic byte verification (prevents MIME spoofing)
    5. Malicious content scan (CVE-known PDF/DOCX vectors)
    6. Filename sanitization (path traversal, null bytes, unsafe chars)
    """
    # 1. User may only upload for themselves
    if user_id != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot upload resume for another user.")

    settings = get_settings()

    # Rate limiting with Redis
    try:
        redis_client = redis.Redis.from_url(settings.redis.redis_url, decode_responses=True)
        rate_key = f"rate_limit:resume_upload:{user_id}"
        uploads = await redis_client.incr(rate_key)
        if uploads == 1:
            await redis_client.expire(rate_key, 3600)  # 1 hour
        elif uploads > 5:
            raise HTTPException(status_code=429, detail="Too many uploads. Please try again later.")
    except redis.RedisError:
        # If Redis fails, log it or fallback (we'll let it pass for now)
        pass
    finally:
        await redis_client.aclose()

    # 2. Extension check
    original_name = file.filename or "resume"
    sanitized_name = _sanitize_filename(original_name)
    ext = Path(sanitized_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    # 3. Content-Type check
    content_type = (file.content_type or "").split(";")[0].strip()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid content type.")

    # 4. Read file — enforce size cap
    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")
    if len(content) < 4:
        raise HTTPException(status_code=400, detail="File is too small to be valid.")

    # 5. Magic byte verification
    if not _validate_magic(ext, content):
        raise HTTPException(
            status_code=400,
            detail="File content does not match its declared extension.",
        )

    # 6. Threat scan
    threat: str | None = None
    if ext == ".pdf":
        threat = _scan_pdf_threats(content)
    elif ext == ".docx":
        threat = _scan_docx_threats(content)
    if threat:
        raise HTTPException(status_code=400, detail=threat)

    # 7. Upload to MinIO
    s3_key = f"resumes/{user_id}/{sanitized_name}"

    try:
        content_type_upload = (
            "application/pdf"
            if ext == ".pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        bucket_name = settings.minio.minio_bucket

        def _upload_to_minio():
            # Check and create bucket if missing
            try:
                s3_client.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                # MinIO / S3 returns 404 or NoSuchBucket
                if str(error_code) in ("404", "NoSuchBucket"):
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    raise

            # Upload the file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=content_type_upload,
            )

        from orchestration.core.spans import traced
        from orchestration.core.metrics import minio_upload_total
        
        loop = asyncio.get_event_loop()
        async with traced("MinIO Upload"):
            await loop.run_in_executor(None, _upload_to_minio)
        minio_upload_total.add(1, {"result": "success"})
    except ClientError as exc:
        from orchestration.core.metrics import minio_upload_total
        minio_upload_total.add(1, {"result": "failure"})
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {exc}") from exc

    # 8. Database persistence
    try:
        user_uuid = uuid.UUID(user_id)
        result = await _session.execute(select(MasterResume).where(MasterResume.user_id == user_uuid))
        existing_resume = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing_resume:
            existing_resume.file_name = sanitized_name
            existing_resume.file_path = s3_key
            existing_resume.updated_at = now
        else:
            new_resume = MasterResume(
                user_id=user_uuid,
                file_name=sanitized_name,
                file_path=s3_key,
                parsed_json={},
                created_at=now,
                updated_at=now
            )
            _session.add(new_resume)
        await _session.commit()
    except Exception as e:
        await _session.rollback()
        raise HTTPException(status_code=500, detail=f"Database update failed: {e}")

    from orchestration.core.metrics import resume_upload_total
    resume_upload_total.add(1)
    
    return ResumeUploadResponse(s3_key=s3_key, file_name=sanitized_name)


class PreviewResumeResponse(BaseModel):
    url: str

@router.get(
    "/preview",
    response_model=PreviewResumeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def preview_resume(
    current_user: UserRecord = Depends(get_current_user),
    _session: AsyncSession = Depends(get_db_session),
    s3_client = Depends(get_external_s3_client),
) -> PreviewResumeResponse:
    """Generate a pre-signed MinIO URL to preview the uploaded resume."""
    result = await _session.execute(select(MasterResume).where(MasterResume.user_id == current_user.user_id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded")

    settings = get_settings()
    
    try:
        from orchestration.core.spans import traced
        from orchestration.core.metrics import minio_download_total
        async with traced("MinIO Download Presigned URL"):
            import mimetypes
            content_type = mimetypes.guess_type(resume.file_path)[0] or "application/octet-stream"
            content_disposition = "inline" if content_type == "application/pdf" else f"attachment; filename=\"{resume.file_name}\""
            
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.minio.minio_bucket, 
                    'Key': resume.file_path,
                    'ResponseContentType': content_type,
                    'ResponseContentDisposition': content_disposition
                },
                ExpiresIn=3600
            )
        minio_download_total.add(1)
        
        from orchestration.core.metrics import resume_download_total
        resume_download_total.add(1)
        
        return PreviewResumeResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview url: {e}")
