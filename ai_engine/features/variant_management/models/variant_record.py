"""VariantRecord — immutable metadata schema for a generated variant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ai_engine.core.types import ApprovalStatus


class VariantRecord(BaseModel):
    """Immutable metadata record for a generated resume variant.

    Created once at generation time. Approval status is the only mutable field
    (updated via registry, not by modifying this object).
    """

    variant_id: str = Field(description="Unique variant identifier (UUID).")
    job_id: str = Field(description="Job listing this variant was generated for.")
    user_id: str = Field(description="User who owns this variant.")
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt_version: str = Field(default="")
    match_score: int = Field(default=0, ge=0, le=100)
    fabrication_check_result: str = Field(default="passed")  # passed | failed
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    output_file_paths: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}
