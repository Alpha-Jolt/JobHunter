"""Storage service — Phase 0 local file storage stub."""

from __future__ import annotations

import shutil
from pathlib import Path


class StorageService:
    """Phase 0/1 storage: uploads files to MinIO (S3) or falls back to local output directory.

    Args:
        output_dir: Root directory for stored files (fallback).
        s3_client: Optional boto3 S3 client.
        bucket_name: Optional S3 bucket name.
    """

    def __init__(self, output_dir: str = "ai_output", s3_client=None, bucket_name: str = None) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    async def upload_file(self, file_path: str, destination_key: str) -> str:
        """Upload a file to S3 or copy to the local output directory.

        Args:
            file_path: Source file path.
            destination_key: Destination path/key within bucket or output_dir.

        Returns:
            The destination key, or empty string if no file.
        """
        import asyncio
        if not file_path:
            return ""
        src = Path(file_path)
        if not src.is_file():
            return ""
            
        if self.s3_client and self.bucket_name:
            def _upload():
                # Ensure bucket exists before uploading
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket_name)
                except Exception:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                # Let boto3 exceptions propagate so callers can handle storage failures
                self.s3_client.upload_file(str(src), self.bucket_name, destination_key)

            await asyncio.get_event_loop().run_in_executor(None, _upload)
            return destination_key
        else:
            dest = self._output_dir / destination_key
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return destination_key

