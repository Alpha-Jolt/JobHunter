"""File signed-URL endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Query

from controllers.file_controller import get_signed_url
from dependencies import get_minio_uploader
from models.schemas import SignedUrlResponse

router = APIRouter()


@router.get("/signed-url", response_model=SignedUrlResponse)
async def signed_url(
    s3_key: str = Query(..., description="S3 object key"),
    expires_in_hours: int = Query(24, ge=1, le=168),
    uploader=Depends(get_minio_uploader),
):
    if uploader is None:
        raise HTTPException(status_code=503, detail="MinIO not available")
    result = await get_signed_url(uploader, s3_key, expires_in_hours)
    if result is None:
        raise HTTPException(status_code=404, detail=f"File '{s3_key}' not found in storage")
    return result
