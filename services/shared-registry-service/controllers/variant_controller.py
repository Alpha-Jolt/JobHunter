"""Translate VariantRecord ↔ VariantResponse and handle creation."""

import uuid

from models.schemas import CreateVariantRequest, VariantResponse


def variant_to_response(variant) -> VariantResponse:
    d = variant.to_dict()
    return VariantResponse(
        variant_id=d["variant_id"],
        user_id=d["user_id"],
        job_id=d["job_id"],
        master_resume_id=d["master_resume_id"],
        pdf_key=d.get("pdf_key", ""),
        docx_key=d.get("docx_key", ""),
        cover_letter_key=d.get("cover_letter_key", ""),
        approval_status=d["approval_status"],
        approved_at=d.get("approved_at"),
        created_at=d.get("created_at"),
    )


def build_variant_record(req: CreateVariantRequest):
    """Build a VariantRecord from a CreateVariantRequest."""
    from shared.models.variant_record import VariantRecord

    return VariantRecord(
        variant_id=uuid.uuid4(),
        user_id=req.user_id,
        job_id=uuid.UUID(req.job_id),
        master_resume_id=uuid.UUID(req.master_resume_id),
        pdf_key=req.pdf_key,
        docx_key=req.docx_key,
        cover_letter_key=req.cover_letter_key,
        curated_json=req.curated_json,
        gaps_identified=req.gaps_identified or [],
        approval_status=req.approval_status,
    )
