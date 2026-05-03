"""Translate ApplicationRecord ↔ ApplicationResponse and handle creation."""

import uuid

from models.schemas import ApplicationResponse, CreateApplicationRequest


def application_to_response(app) -> ApplicationResponse:
    d = app.to_dict()
    return ApplicationResponse(
        application_id=d["application_id"],
        user_id=d["user_id"],
        job_id=d["job_id"],
        resume_variant_id=d["resume_variant_id"],
        cover_letter_id=d.get("cover_letter_id"),
        status=d["status"],
        sent_at=d["sent_at"],
        last_activity_at=d.get("last_activity_at"),
        reply_count=d.get("reply_count", 0),
    )


def build_application_record(req: CreateApplicationRequest):
    """Build an ApplicationRecord from a CreateApplicationRequest."""
    from shared.models.application_record import ApplicationRecord

    cover_letter_id = uuid.UUID(req.cover_letter_id) if req.cover_letter_id else None
    return ApplicationRecord(
        application_id=uuid.uuid4(),
        user_id=req.user_id,
        job_id=uuid.UUID(req.job_id),
        resume_variant_id=uuid.UUID(req.resume_variant_id),
        cover_letter_id=cover_letter_id,
        email_subject=req.email_subject,
    )
