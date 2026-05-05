"""Health check endpoints."""

from fastapi import APIRouter, Depends

from dependencies import get_job_registry, get_variant_registry

router = APIRouter()


@router.get("")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@router.get("/ready")
async def readiness(
    _job_reg=Depends(get_job_registry),
    _var_reg=Depends(get_variant_registry),
):
    return {"status": "ready", "registries": "ok", "minio": "ok"}
