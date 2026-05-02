"""MinIO S3 uploader for resume and cover letter files."""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import structlog

logger = structlog.get_logger(__name__)


class MinIOUploadError(Exception):
    """Raised when MinIO upload fails."""

    pass


class MinIOUploader:
    """Uploads files to MinIO S3 and returns object keys."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str = "jobhunter-resumes",
        use_ssl: bool = False,
    ) -> None:
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.use_ssl = use_ssl
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if use_ssl else 'http'}://{endpoint}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
        )
        self._bucket_ready = False

    async def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        if self._bucket_ready:
            return
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._check_and_create_bucket)
            self._bucket_ready = True
            logger.info("minio.bucket_ready", bucket=self.bucket_name)
        except ClientError as e:
            raise MinIOUploadError(f"Cannot access bucket '{self.bucket_name}': {e}") from e

    def _check_and_create_bucket(self) -> None:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info("minio.bucket_created", bucket=self.bucket_name)
            else:
                raise

    async def upload_file(
        self,
        local_path: Path,
        user_id: str,
        job_id: str,
        file_type: str,
    ) -> str:
        """Upload file to MinIO and return S3 key.

        Args:
            local_path: Path to local file.
            user_id: User UUID string.
            job_id: Job UUID string.
            file_type: One of "resume_pdf", "resume_docx", "cover_letter".

        Returns:
            S3 object key.

        Raises:
            MinIOUploadError: If upload fails.
        """
        await self._ensure_bucket_exists()
        if not local_path.exists():
            raise MinIOUploadError(f"File not found: {local_path}")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        s3_key = f"resumes/{user_id}/{job_id}/{timestamp}_{file_type}{local_path.suffix}"

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._upload_file_sync, local_path, s3_key)
            logger.info("minio.uploaded", file=local_path.name, key=s3_key)
            return s3_key
        except (ClientError, NoCredentialsError) as e:
            raise MinIOUploadError(f"Upload failed: {e}") from e

    def _upload_file_sync(self, local_path: Path, s3_key: str) -> None:
        self.s3_client.upload_file(
            str(local_path),
            self.bucket_name,
            s3_key,
            ExtraArgs={"ContentType": self._get_content_type(local_path)},
        )

    @staticmethod
    def _get_content_type(file_path: Path) -> str:
        return {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".txt": "text/plain",
        }.get(file_path.suffix, "application/octet-stream")

    async def get_signed_url(self, s3_key: str, expires_in_hours: int = 24) -> str:
        """Generate a presigned URL for temporary file access."""
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                None, self._generate_presigned_url, s3_key, expires_in_hours
            )
        except ClientError as e:
            raise MinIOUploadError(f"Signed URL generation failed: {e}") from e

    def _generate_presigned_url(self, s3_key: str, expires_in_hours: int) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expires_in_hours * 3600,
        )

    async def verify_upload(self, s3_key: str) -> bool:
        """Return True if the object exists in MinIO."""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None, self.s3_client.head_object, self.bucket_name, s3_key
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise MinIOUploadError(f"Verification failed: {e}") from e
