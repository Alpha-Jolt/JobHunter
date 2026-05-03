"""Pydantic request/response schemas."""

from typing import List, Optional

from pydantic import BaseModel


# ===== Job =====

class JobResponse(BaseModel):
    job_id: str
    source: str
    external_id: str
    title: str
    company_name: str
    company_domain: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    description: str
    skills_required: List[str] = []
    job_type: str
    apply_email: Optional[str] = None
    email_trust: str
    apply_url: Optional[str] = None
    posted_at: Optional[str] = None
    scraped_at: Optional[str] = None
    last_seen_at: Optional[str] = None
    status: str


# ===== Variant =====

class CreateVariantRequest(BaseModel):
    user_id: str
    job_id: str
    master_resume_id: str
    pdf_key: str = ""
    docx_key: str = ""
    cover_letter_key: str = ""
    curated_json: dict
    gaps_identified: Optional[List] = None
    approval_status: str = "pending"


class UpdateVariantApprovalRequest(BaseModel):
    approval_status: str
    approval_token: Optional[str] = None


class VariantResponse(BaseModel):
    variant_id: str
    user_id: str
    job_id: str
    master_resume_id: str
    pdf_key: str
    docx_key: str
    cover_letter_key: str
    approval_status: str
    approved_at: Optional[str] = None
    created_at: Optional[str] = None


# ===== Application =====

class CreateApplicationRequest(BaseModel):
    user_id: str
    job_id: str
    resume_variant_id: str
    cover_letter_id: Optional[str] = None
    email_subject: str


class UpdateApplicationStatusRequest(BaseModel):
    status: str
    reply_count: Optional[int] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    application_id: str
    user_id: str
    job_id: str
    resume_variant_id: str
    cover_letter_id: Optional[str] = None
    status: str
    sent_at: str
    last_activity_at: Optional[str] = None
    reply_count: int


# ===== Files =====

class SignedUrlResponse(BaseModel):
    signed_url: str
    expires_at: str
    s3_key: str
