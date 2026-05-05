"""Job endpoints."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from controllers.job_controller import job_to_response
from dependencies import get_job_registry
from models.schemas import JobResponse

router = APIRouter()


@router.get("/all-with-email", response_model=List[JobResponse])
async def get_all_with_email(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    registry=Depends(get_job_registry),
):
    jobs = await registry.get_all_with_email()
    return [job_to_response(j) for j in jobs[offset: offset + limit]]


@router.get("/by-source/{source}", response_model=List[JobResponse])
async def get_jobs_by_source(
    source: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    registry=Depends(get_job_registry),
):
    jobs = await registry.get_by_source(source)
    return [job_to_response(j) for j in jobs[offset: offset + limit]]


@router.get("/status/{status}", response_model=List[JobResponse])
async def get_jobs_by_status(
    status: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    registry=Depends(get_job_registry),
):
    jobs = await registry.get_by_status(status)
    return [job_to_response(j) for j in jobs[offset: offset + limit]]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, registry=Depends(get_job_registry)):
    try:
        job = await registry.get(uuid.UUID(job_id))
        return job_to_response(job)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    except Exception:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
