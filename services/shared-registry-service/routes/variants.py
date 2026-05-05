"""Variant endpoints."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from controllers.variant_controller import build_variant_record, variant_to_response
from dependencies import get_variant_registry
from models.schemas import CreateVariantRequest, UpdateVariantApprovalRequest, VariantResponse

router = APIRouter()

_VALID_APPROVAL_STATUSES = {"approved", "rejected", "pending"}


@router.get("/approved/{job_id}/{user_id}", response_model=VariantResponse)
async def get_approved_variant(
    job_id: str,
    user_id: str,
    registry=Depends(get_variant_registry),
):
    try:
        variant = await registry.get_approved_for_job(uuid.UUID(job_id), user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    if not variant:
        raise HTTPException(status_code=404, detail="No approved variant found")
    return variant_to_response(variant)


@router.get("/for-user/{user_id}", response_model=List[VariantResponse])
async def get_variants_for_user(
    user_id: str,
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    registry=Depends(get_variant_registry),
):
    variants = await registry.get_for_user(user_id)
    if status:
        variants = [v for v in variants if v.approval_status == status]
    return [variant_to_response(v) for v in variants[offset: offset + limit]]


@router.get("/{variant_id}", response_model=VariantResponse)
async def get_variant(variant_id: str, registry=Depends(get_variant_registry)):
    try:
        variant = await registry.get(uuid.UUID(variant_id))
        return variant_to_response(variant)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid variant_id format")
    except Exception:
        raise HTTPException(status_code=404, detail=f"Variant '{variant_id}' not found")


@router.post("", response_model=VariantResponse, status_code=201)
async def create_variant(req: CreateVariantRequest, registry=Depends(get_variant_registry)):
    try:
        record = build_variant_record(req)
        await registry.save(record)
        return variant_to_response(record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.patch("/{variant_id}/approval", response_model=VariantResponse)
async def update_approval(
    variant_id: str,
    req: UpdateVariantApprovalRequest,
    registry=Depends(get_variant_registry),
):
    if req.approval_status not in _VALID_APPROVAL_STATUSES:
        raise HTTPException(
            status_code=400, detail=f"Invalid approval_status: {req.approval_status!r}"
        )
    try:
        vid = uuid.UUID(variant_id)
        await registry.update_approval_status(vid, req.approval_status)
        variant = await registry.get(vid)
        return variant_to_response(variant)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid variant_id format")
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
