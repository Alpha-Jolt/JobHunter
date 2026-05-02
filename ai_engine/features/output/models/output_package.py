"""OutputPackage — final deliverable schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OutputPackage(BaseModel):
    """All output files generated for an approved variant."""

    variant_id: str
    job_id: str
    resume_docx_path: str = ""
    resume_pdf_path: str = ""
    cover_letter_pdf_path: str = ""
    email_draft_path: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    manifest: dict = Field(default_factory=dict, description="Metadata about all outputs.")

    model_config = {"frozen": True}
