"""Generate MinIO signed URLs."""

from datetime import datetime, timedelta, timezone

from models.schemas import SignedUrlResponse


async def get_signed_url(uploader, s3_key: str, expires_in_hours: int) -> SignedUrlResponse:
    try:
        exists = await uploader.verify_upload(s3_key)
    except Exception:
        return None
    if not exists:
        return None
    signed_url = await uploader.get_signed_url(s3_key, expires_in_hours)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).isoformat()
    return SignedUrlResponse(signed_url=signed_url, expires_at=expires_at, s3_key=s3_key)
