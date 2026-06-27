"""Storage service — Phase 0 local file storage stub."""

from __future__ import annotations

import shutil
from pathlib import Path


class StorageService:
    """Phase 0 storage: copies files to a local output directory.

    Args:
        output_dir: Root directory for stored files.
    """

    def __init__(self, output_dir: str = "ai_output") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, file_path: str, destination_key: str) -> str:
        """Copy a file to the local output directory.

        Args:
            file_path: Source file path.
            destination_key: Relative destination path within output_dir.

        Returns:
            The destination key (local path relative to output_dir), or empty string if no file.
        """
        if not file_path:
            return ""
        src = Path(file_path)
        if not src.is_file():
            return ""
        dest = self._output_dir / destination_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return destination_key
