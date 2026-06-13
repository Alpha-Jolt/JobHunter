"""Base policy abstract class."""

from __future__ import annotations

from abc import ABC

from orchestration.auth.models.user import UserRecord


class BasePolicy(ABC):
    """Abstract base for all policy classes.

    Policies encode multi-condition business rules that go beyond
    a simple role check. Each method returns True/False.
    """

    @staticmethod
    def _is_admin(user: UserRecord) -> bool:
        from orchestration.auth.models.user import RoleEnum
        return user.role == RoleEnum.ADMIN
