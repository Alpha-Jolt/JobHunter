"""Approval status models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ai_engine.core.types import ApprovalMethod, ApprovalStatus


class ApprovalMetadata(BaseModel):
    """Metadata recorded when a variant is approved or rejected."""

    variant_id: str
    status: ApprovalStatus
    approval_method: ApprovalMethod = ApprovalMethod.CLI
    approver_id: str = ""
    approval_timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ""

    model_config = {"frozen": True}
