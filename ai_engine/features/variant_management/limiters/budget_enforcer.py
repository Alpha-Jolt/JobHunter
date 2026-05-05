"""Budget enforcer — hard variant generation limits."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ai_engine.core.exceptions import VariantBudgetExceededError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)


class BudgetStatus(str, Enum):
    """Budget availability status."""

    AVAILABLE = "available"
    APPROACHING_LIMIT = "approaching_limit"
    LIMIT_REACHED = "limit_reached"


@dataclass
class BudgetCheckResult:
    """Result of a budget check.

    Attributes:
        status: Current budget status.
        total_used: Total variants generated so far.
        total_limit: Maximum allowed variants.
        session_used: Variants generated in this session.
        session_limit: Maximum variants per session.
    """

    status: BudgetStatus
    total_used: int
    total_limit: int
    session_used: int
    session_limit: int


class BudgetEnforcer:
    """Enforces variant generation budget limits.

    Args:
        max_total: Maximum total variants allowed.
        max_per_session: Maximum variants per session.
        warning_threshold: Fraction at which to warn (e.g. 0.8 = 80%).
    """

    def __init__(
        self,
        max_total: int,
        max_per_session: int,
        warning_threshold: float = 0.8,
    ) -> None:
        self._max_total = max_total
        self._max_per_session = max_per_session
        self._warning_threshold = warning_threshold
        self._session_count = 0

    def check(self, total_count: int) -> BudgetCheckResult:
        """Check current budget status without consuming a slot.

        Args:
            total_count: Current total variant count from the registry.

        Returns:
            BudgetCheckResult with current status.
        """
        if total_count >= self._max_total or self._session_count >= self._max_per_session:
            status = BudgetStatus.LIMIT_REACHED
        elif (
            total_count / self._max_total >= self._warning_threshold
            or self._session_count / self._max_per_session >= self._warning_threshold
        ):
            status = BudgetStatus.APPROACHING_LIMIT
        else:
            status = BudgetStatus.AVAILABLE

        return BudgetCheckResult(
            status=status,
            total_used=total_count,
            total_limit=self._max_total,
            session_used=self._session_count,
            session_limit=self._max_per_session,
        )

    def consume(self, total_count: int) -> None:
        """Consume one budget slot, raising if limit is reached.

        Args:
            total_count: Current total variant count from the registry.

        Raises:
            VariantBudgetExceededError: If either limit is reached.
        """
        result = self.check(total_count)
        if result.status == BudgetStatus.LIMIT_REACHED:
            raise VariantBudgetExceededError(
                f"Variant budget exceeded: {total_count}/{self._max_total} total, "
                f"{self._session_count}/{self._max_per_session} this session."
            )
        if result.status == BudgetStatus.APPROACHING_LIMIT:
            logger.warning(
                "budget_enforcer.approaching_limit",
                total_used=total_count,
                total_limit=self._max_total,
                session_used=self._session_count,
                session_limit=self._max_per_session,
            )
        self._session_count += 1
