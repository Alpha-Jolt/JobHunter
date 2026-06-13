"""Job policy — authorization rules for job records."""

from __future__ import annotations

import uuid
from typing import Any

from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.policies.base import BasePolicy


class JobPolicy(BasePolicy):
    """Authorization rules for Job resources."""

    @staticmethod
    def can_create(user: UserRecord) -> bool:
        """Recruiter or Admin can create a job posting.

        Scraper-created jobs bypass this (internal path, no user auth).
        """
        return user.role in (RoleEnum.RECRUITER, RoleEnum.ADMIN)

    @staticmethod
    def can_update(user: UserRecord, job: Any) -> bool:
        """Recruiter owns the job AND job is not closed, OR Admin.

        Args:
            user: Authenticated user.
            job: Any object with recruiter_id (UUID|None) and status (str).
        """
        if BasePolicy._is_admin(user):
            return True
        if user.role != RoleEnum.RECRUITER:
            return False
        recruiter_id = getattr(job, "recruiter_id", None)
        if recruiter_id is None:
            return False  # scraper-owned job — not user-editable
        if isinstance(recruiter_id, str):
            try:
                recruiter_id = uuid.UUID(recruiter_id)
            except ValueError:
                return False
        status = getattr(job, "status", "")
        return recruiter_id == user.user_id and status != "closed"

    @staticmethod
    def can_close(user: UserRecord, job: Any, active_application_count: int = 0) -> bool:
        """Recruiter owns the job AND no active applications, OR Admin.

        Args:
            user: Authenticated user.
            job: Job object with recruiter_id and status.
            active_application_count: Number of applications not in terminal state.
        """
        if BasePolicy._is_admin(user):
            return True
        if not JobPolicy.can_update(user, job):
            return False
        return active_application_count == 0
