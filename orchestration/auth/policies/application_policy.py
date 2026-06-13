"""Application policy — authorization rules for ApplicationLog records."""

from __future__ import annotations

import uuid
from typing import Any

from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.policies.base import BasePolicy


class ApplicationPolicy(BasePolicy):
    """Authorization rules for ApplicationLog resources."""

    @staticmethod
    def can_view(user: UserRecord, application: Any, job: Any = None) -> bool:
        """User owns the application, OR the Recruiter posted the job, OR Admin.

        Args:
            user: Authenticated user.
            application: Object with user_id (UUID).
            job: Optional job object with recruiter_id (UUID|None).
        """
        if BasePolicy._is_admin(user):
            return True

        app_user_id = getattr(application, "user_id", None)
        if isinstance(app_user_id, str):
            try:
                app_user_id = uuid.UUID(app_user_id)
            except ValueError:
                pass
        if app_user_id == user.user_id:
            return True

        # Recruiter who posted the job can view incoming applications
        if user.role == RoleEnum.RECRUITER and job is not None:
            recruiter_id = getattr(job, "recruiter_id", None)
            if isinstance(recruiter_id, str):
                try:
                    recruiter_id = uuid.UUID(recruiter_id)
                except ValueError:
                    return False
            return recruiter_id == user.user_id

        return False

    @staticmethod
    def can_update_status(user: UserRecord, application: Any, job: Any) -> bool:
        """Only the Recruiter who posted the job can update application status, OR Admin.

        Args:
            user: Authenticated user.
            application: ApplicationLog object (unused directly, reserved for future).
            job: Job object with recruiter_id.
        """
        if BasePolicy._is_admin(user):
            return True
        if user.role != RoleEnum.RECRUITER:
            return False
        recruiter_id = getattr(job, "recruiter_id", None)
        if isinstance(recruiter_id, str):
            try:
                recruiter_id = uuid.UUID(recruiter_id)
            except ValueError:
                return False
        return recruiter_id == user.user_id
