"""Pipeline configuration schema."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from ai_engine.core.types import PipelineMode


class PipelineConfig(BaseModel):
    """Configuration for a single pipeline execution."""

    scraper_output_dir: Path = Path("output/final")
    ai_output_dir: Path = Path("ai_output")
    resume_file_path: Path = Field(description="Path to the candidate's resume file.")
    job_ids_to_process: list[str] = Field(
        default_factory=list,
        description="Specific job IDs to process. Empty list means process all.",
    )
    user_id: str = Field(description="User identifier.")
    session_id: str = Field(description="Unique session identifier.")
    mode: PipelineMode = PipelineMode.GENERATE
    auto_approve: bool = Field(
        default=False,
        description="Auto-approve all variants (for testing only).",
    )
    email_template_path: Path | None = None
    variant_ids_to_release: list[str] = Field(
        default_factory=list,
        description="Variant IDs to release in RELEASE mode.",
    )

    @field_validator("resume_file_path", "email_template_path", mode="after")
    @classmethod
    def _no_path_traversal(cls, v: Path | None) -> Path | None:
        if v is None:
            return v
        try:
            resolved = v.resolve()
            cwd = Path.cwd().resolve()
            if not str(resolved).startswith(str(cwd)):
                raise ValueError(
                    "Path traversal detected: path must be within the working directory."
                )
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")
        return v
