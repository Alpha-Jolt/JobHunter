"""Application endpoints."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from controllers.application_controller import (
    application_to_response,
    build_application_record,
)
from dependencies import get_application_log
from models.schemas import (
    ApplicationResponse,
    CreateApplicationRequest,
    UpdateApplicationStatusRequest,
)

router = APIRouter()


@router.get("/by-user/{user_id}", response_model=List[ApplicationResponse])
async def get_applications_by_user(
    user_id: str,
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    log=Depends(get_application_log),
):
    apps = await log.get_by_user(user_id)
    if status:
        apps = [a for a in apps if a.status == status]
    return [application_to_response(a) for a in apps[offset: offset + limit]]


@router.get("/by-job/{job_id}", response_model=List[ApplicationResponse])
async def get_applications_by_job(
    job_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    log=Depends(get_application_log),
):
    try:
        apps = await log.get_by_job(uuid.UUID(job_id))
        return [application_to_response(a) for a in apps[offset: offset + limit]]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")


@router.get("/sent-today/{user_id}", response_model=List[ApplicationResponse])
async def get_sent_today(user_id: str, log=Depends(get_application_log)):
    apps = await log.get_applications_sent_today(user_id)
    return [application_to_response(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, log=Depends(get_application_log)):
    try:
        app = await log.get(uuid.UUID(application_id))
        return application_to_response(app)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application_id format")
    except Exception:
        raise HTTPException(status_code=404, detail=f"Application '{application_id}' not found")


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(req: CreateApplicationRequest, log=Depends(get_application_log)):
    try:
        record = build_application_record(req)
        await log.record_send(record)
        return application_to_response(record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str,
    req: UpdateApplicationStatusRequest,
    log=Depends(get_application_log),
):
    try:
        aid = uuid.UUID(application_id)
        await log.update_status(aid, req.status)
        if req.reply_count is not None:
            await log.update_reply_count(aid, req.reply_count)
        app = await log.get(aid)
        return application_to_response(app)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application_id format")
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
