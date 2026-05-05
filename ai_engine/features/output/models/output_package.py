"""OutputPackage — final deliverable schema."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class OutputPackage(BaseModel):
    """All output files generated for an approved variant."""

    variant_id: str
    job_id: str
    resume_docx_path: str = ""
    resume_pdf_path: str = ""
    cover_letter_pdf_path: str = ""
    email_draft_path: str = ""
    pdf_s3_key: str = ""
    docx_s3_key: str = ""
    cover_letter_s3_key: str = ""
    s3_upload_failed: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    manifest: dict = Field(default_factory=dict, description="Metadata about all outputs.")

    model_config = {"frozen": True}
