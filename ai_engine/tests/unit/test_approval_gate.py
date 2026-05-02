"""Unit tests for approval gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_engine.core.exceptions import ApprovalRequiredError
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.approval.approval_gate import ApprovalGate
from ai_engine.features.variant_management.models.variant_record import VariantRecord
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry


def _register_variant(registry: JSONRegistry, variant_id: str, status: ApprovalStatus) -> None:
    record = VariantRecord(
        variant_id=variant_id,
        job_id="job-001",
        user_id="user-1",
        approval_status=status,
    )
    registry.create(record)


def test_approval_gate_passes_approved_variant(tmp_path: Path):
    """Gate allows approved variants through."""
    registry = JSONRegistry(tmp_path / "registry.json")
    _register_variant(registry, "v-001", ApprovalStatus.APPROVED)

    gate = ApprovalGate(registry)
    gate.require_approved("v-001")  # Should not raise


def test_approval_gate_blocks_pending_variant(tmp_path: Path):
    """Gate raises ApprovalRequiredError for pending variants."""
    registry = JSONRegistry(tmp_path / "registry.json")
    _register_variant(registry, "v-002", ApprovalStatus.PENDING)

    gate = ApprovalGate(registry)
    with pytest.raises(ApprovalRequiredError):
        gate.require_approved("v-002")


def test_approval_gate_blocks_rejected_variant(tmp_path: Path):
    """Gate raises ApprovalRequiredError for rejected variants."""
    registry = JSONRegistry(tmp_path / "registry.json")
    _register_variant(registry, "v-003", ApprovalStatus.REJECTED)

    gate = ApprovalGate(registry)
    with pytest.raises(ApprovalRequiredError):
        gate.require_approved("v-003")


def test_approval_gate_blocks_unknown_variant(tmp_path: Path):
    """Gate raises ApprovalRequiredError for unknown variant IDs."""
    registry = JSONRegistry(tmp_path / "registry.json")
    gate = ApprovalGate(registry)

    with pytest.raises(ApprovalRequiredError):
        gate.require_approved("nonexistent-variant")
