"""File I/O and path management utilities."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create directory and all parents if they don't exist.

    Args:
        path: Directory path to create.

    Returns:
        The same path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_files(directory: Path, extensions: tuple[str, ...] = (".csv", ".json")) -> list[Path]:
    """List files in a directory matching given extensions.

    Args:
        directory: Directory to search.
        extensions: Tuple of file extensions to include (e.g. ('.csv', '.json')).

    Returns:
        Sorted list of matching file paths.
    """
    if not directory.exists():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in extensions)
