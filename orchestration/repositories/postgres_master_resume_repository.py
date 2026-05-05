"""PostgreSQL-backed MasterResume repository."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgresMasterResumeRepository:
    """Stores and retrieves parsed master resumes.

    Args:
        session: An active AsyncSession instance.
        resume_parser: AI Engine ResumeParser instance (optional; used for parsing).
    """

    def __init__(self, session: AsyncSession, resume_parser=None) -> None:
        self._session = session
        self._resume_parser = resume_parser

    async def get_or_create(
        self,
        user_id: str,
        file_path: str,
    ) -> Tuple[uuid.UUID, dict, str]:
        """Return existing parsed resume or parse and store a new one.

        Args:
            user_id: User identifier.
            file_path: Path to the resume file.

        Returns:
            Tuple of (resume_id, parsed_json, prompt_version).
        """
        import orchestration.db.models as _m
        MasterResume = _m.MasterResume

        file_name = Path(file_path).name

        # Check if already stored for this user+file
        result = await self._session.execute(
            select(MasterResume).where(
                MasterResume.user_id == user_id,
                MasterResume.file_name == file_name,
            )
        )
        row = result.scalar_one_or_none()
        if row is not None:
            return uuid.UUID(str(row.resume_id)), dict(row.parsed_json or {}), ""

        # Parse and store
        parsed_json: dict = {}
        prompt_version = ""
        if self._resume_parser is not None:
            resume_data = await self._resume_parser.parse(Path(file_path))
            parsed_json = resume_data.model_dump(exclude={"raw_text"})
            prompt_version = ""

        resume_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        row = MasterResume(
            resume_id=str(resume_id),
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            parsed_json=parsed_json,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        await self._session.flush()

        return resume_id, parsed_json, prompt_version
