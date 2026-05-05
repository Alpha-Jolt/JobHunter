"""Pipeline result schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PipelineResult(BaseModel):
    """Result of a pipeline execution."""

    status: str = Field(description="success | partial_failure | failure")
    generated_variants: int = 0
    output_packages: int = 0
    errors: list[str] = Field(default_factory=list)
    execution_summary: str = ""
    variant_ids: list[str] = Field(default_factory=list)
    output_paths: list[str] = Field(default_factory=list)
