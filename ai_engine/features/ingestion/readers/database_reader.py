"""Database reader stub — Phase 0+ PostgreSQL integration point."""

from __future__ import annotations


def read_database(  # type: ignore[return]
    connection_string: str,
    query: str | None = None,
) -> list:
    """Read job records from PostgreSQL (Phase 0+ stub).

    Args:
        connection_string: PostgreSQL connection string.
        query: Optional SQL query override.

    Raises:
        NotImplementedError: Always — PostgreSQL integration is Phase 0+.
    """
    raise NotImplementedError(
        "Database reader is a Phase 0+ feature. Use csv_reader or json_reader for Phase 0."
    )
