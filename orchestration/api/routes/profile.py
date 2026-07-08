import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, HttpUrl
from uuid import UUID
import magic

from orchestration.api.dependencies import get_profile_repo, get_internal_s3_client
from orchestration.auth.dependencies import get_current_user, require_role
from orchestration.db.models import User, user_role
from orchestration.api.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────────────────

class UserExperienceSchema(BaseModel):
    exp_id: Optional[UUID] = None
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    location: Optional[str] = None
    order_index: int = 0

class UserEducationSchema(BaseModel):
    edu_id: Optional[UUID] = None
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    order_index: int = 0

class UserProjectSchema(BaseModel):
    proj_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    repo_url: Optional[str] = None
    skills: List[str] = []
    order_index: int = 0

class UserCertificationSchema(BaseModel):
    cert_id: Optional[UUID] = None
    name: str
    issuer: Optional[str] = None
    issued_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_url: Optional[str] = None
    order_index: int = 0

class UserSkillSchema(BaseModel):
    skill_id: Optional[UUID] = None
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    order_index: int = 0

class UserLanguageSchema(BaseModel):
    lang_id: Optional[UUID] = None
    name: str
    proficiency: Optional[str] = None
    order_index: int = 0

class UserAchievementSchema(BaseModel):
    ach_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    order_index: int = 0

class UserSocialLinkSchema(BaseModel):
    link_id: Optional[UUID] = None
    platform: str
    url: str
    order_index: int = 0

class UserProfileUpsertSchema(BaseModel):
    username: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    is_public: Optional[bool] = None

class UserProfileFullSchema(BaseModel):
    user_id: UUID
    username: str
    headline: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    website_url: Optional[str]
    avatar_url: Optional[str] = None
    is_public: bool
    public_slug: Optional[str]
    experiences: List[UserExperienceSchema]
    education: List[UserEducationSchema]
    projects: List[UserProjectSchema]
    certifications: List[UserCertificationSchema]
    skills: List[UserSkillSchema]
    languages: List[UserLanguageSchema]
    achievements: List[UserAchievementSchema]
    social_links: List[UserSocialLinkSchema]


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_avatar_url(s3_client, bucket_name: str, object_key: str) -> Optional[str]:
    if not object_key:
        return None
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=3600,
        )
        return url
    except Exception as e:
        logger.warning(f"Could not generate presigned URL for avatar: {e}")
        return None

def _map_profile_to_schema(profile, s3_client, bucket_name: str) -> dict:
    avatar_url = _get_avatar_url(s3_client, bucket_name, profile.avatar_key) if profile.avatar_key else None
    return {
        "user_id": profile.user_id,
        "username": profile.username,
        "headline": profile.headline,
        "bio": profile.bio,
        "location": profile.location,
        "website_url": profile.website_url,
        "avatar_url": avatar_url,
        "is_public": profile.is_public,
        "public_slug": profile.public_slug,
        "experiences": [
            {
                "exp_id": e.exp_id, "company": e.company, "title": e.title,
                "start_date": e.start_date.isoformat() if e.start_date else None,
                "end_date": e.end_date.isoformat() if e.end_date else None,
                "is_current": e.is_current, "description": e.description,
                "location": e.location, "order_index": e.order_index
            } for e in profile.experiences
        ],
        "education": [
            {
                "edu_id": e.edu_id, "institution": e.institution, "degree": e.degree,
                "field": e.field, "start_year": e.start_year, "end_year": e.end_year,
                "grade": e.grade, "description": e.description, "order_index": e.order_index
            } for e in profile.education
        ],
        "projects": [
            {
                "proj_id": p.proj_id, "title": p.title, "description": p.description,
                "url": p.url, "repo_url": p.repo_url, "skills": p.skills, "order_index": p.order_index
            } for p in profile.projects
        ],
        "certifications": [
            {
                "cert_id": c.cert_id, "name": c.name, "issuer": c.issuer,
                "issued_date": c.issued_date.isoformat() if c.issued_date else None,
                "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
                "credential_url": c.credential_url, "order_index": c.order_index
            } for c in profile.certifications
        ],
        "skills": [
            {
                "skill_id": s.skill_id, "name": s.name, "category": s.category,
                "proficiency": s.proficiency, "order_index": s.order_index
            } for s in profile.skills
        ],
        "languages": [
            {
                "lang_id": l.lang_id, "name": l.name, "proficiency": l.proficiency, "order_index": l.order_index
            } for l in profile.languages
        ],
        "achievements": [
            {
                "ach_id": a.ach_id, "title": a.title, "description": a.description,
                "date": a.date.isoformat() if a.date else None, "url": a.url, "order_index": a.order_index
            } for a in profile.achievements
        ],
        "social_links": [
            {
                "link_id": s.link_id, "platform": s.platform, "url": s.url, "order_index": s.order_index
            } for s in profile.social_links
        ]
    }

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserProfileFullSchema)
async def get_my_profile(
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo),
    settings = Depends(get_settings),
    s3_client = Depends(get_internal_s3_client)
):
    profile = await repo.get_profile(user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _map_profile_to_schema(profile, s3_client, settings.minio.minio_avatar_bucket)


@router.put("/me", response_model=UserProfileFullSchema)
async def update_my_profile(
    data: UserProfileUpsertSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo),
    settings = Depends(get_settings),
    s3_client = Depends(get_internal_s3_client)
):
    try:
        profile = await repo.upsert_profile(user.user_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Reload with relations
    profile = await repo.get_profile(user.user_id)
    return _map_profile_to_schema(profile, s3_client, settings.minio.minio_avatar_bucket)

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo),
    settings = Depends(get_settings),
    s3_client = Depends(get_internal_s3_client)
):
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    mime = magic.from_buffer(content, mime=True)
    if mime not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
        
    ext = mime.split("/")[1]
    object_key = f"{user.user_id}/avatar_{uuid.uuid4().hex[:8]}.{ext}"
    
    try:
        s3_client.put_object(
            Bucket=settings.minio.minio_avatar_bucket,
            Key=object_key,
            Body=content,
            ContentType=mime,
        )
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload avatar")

    # Update DB
    await repo.upsert_profile(user.user_id, {"avatar_key": object_key})
    
    return {"avatar_url": _get_avatar_url(s3_client, settings.minio.minio_avatar_bucket, object_key)}

@router.delete("/me/avatar")
async def delete_avatar(
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo),
    settings = Depends(get_settings),
    s3_client = Depends(get_internal_s3_client)
):
    profile = await repo.get_profile(user.user_id)
    if profile and profile.avatar_key:
        try:
            s3_client.delete_object(
                Bucket=settings.minio.minio_avatar_bucket,
                Key=profile.avatar_key
            )
        except Exception as e:
            logger.warning(f"S3 delete failed: {e}")
        
        await repo.upsert_profile(user.user_id, {"avatar_key": None})
    return {"status": "ok"}


@router.get("/u/{username}", response_model=UserProfileFullSchema)
async def get_public_profile(
    username: str,
    repo = Depends(get_profile_repo),
    settings = Depends(get_settings),
    s3_client = Depends(get_internal_s3_client)
):
    profile = await repo.get_public_profile(username)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _map_profile_to_schema(profile, s3_client, settings.minio.minio_avatar_bucket)


@router.post("/me/experience")
async def add_experience(
    data: UserExperienceSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    exp = await repo.add_experience(user.user_id, data.model_dump(exclude={'exp_id'}))
    return {"exp_id": exp.exp_id}

@router.put("/me/experience/{exp_id}")
async def update_experience(
    exp_id: UUID,
    data: UserExperienceSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    exp = await repo.update_experience(user.user_id, exp_id, data.model_dump(exclude={'exp_id'}, exclude_unset=True))
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"status": "ok"}

@router.delete("/me/experience/{exp_id}")
async def delete_experience(
    exp_id: UUID,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    success = await repo.delete_experience(user.user_id, exp_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"status": "ok"}


@router.post("/me/education")
async def add_education(
    data: UserEducationSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    edu = await repo.add_education(user.user_id, data.model_dump(exclude={'edu_id'}))
    return {"edu_id": edu.edu_id}

@router.put("/me/education/{edu_id}")
async def update_education(
    edu_id: UUID,
    data: UserEducationSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    edu = await repo.update_education(user.user_id, edu_id, data.model_dump(exclude={'edu_id'}, exclude_unset=True))
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    return {"status": "ok"}

@router.delete("/me/education/{edu_id}")
async def delete_education(
    edu_id: UUID,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    success = await repo.delete_education(user.user_id, edu_id)
    if not success:
        raise HTTPException(status_code=404, detail="Education not found")
    return {"status": "ok"}


@router.post("/me/projects")
async def add_project(
    data: UserProjectSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    proj = await repo.add_project(user.user_id, data.model_dump(exclude={'proj_id'}))
    return {"proj_id": proj.proj_id}

@router.put("/me/projects/{proj_id}")
async def update_project(
    proj_id: UUID,
    data: UserProjectSchema,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    proj = await repo.update_project(user.user_id, proj_id, data.model_dump(exclude={'proj_id'}, exclude_unset=True))
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "ok"}

@router.delete("/me/projects/{proj_id}")
async def delete_project(
    proj_id: UUID,
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    success = await repo.delete_project(user.user_id, proj_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "ok"}


@router.put("/me/skills")
async def replace_skills(
    data: List[UserSkillSchema],
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    await repo.replace_skills(user.user_id, [s.model_dump(exclude={'skill_id'}) for s in data])
    return {"status": "ok"}

@router.put("/me/certifications")
async def replace_certifications(
    data: List[UserCertificationSchema],
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    await repo.replace_certifications(user.user_id, [c.model_dump(exclude={'cert_id'}) for c in data])
    return {"status": "ok"}

@router.put("/me/languages")
async def replace_languages(
    data: List[UserLanguageSchema],
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    await repo.replace_languages(user.user_id, [l.model_dump(exclude={'lang_id'}) for l in data])
    return {"status": "ok"}

@router.put("/me/achievements")
async def replace_achievements(
    data: List[UserAchievementSchema],
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    await repo.replace_achievements(user.user_id, [a.model_dump(exclude={'ach_id'}) for a in data])
    return {"status": "ok"}

@router.put("/me/social-links")
async def replace_social_links(
    data: List[UserSocialLinkSchema],
    user: User = Depends(require_role("hunter")),
    repo = Depends(get_profile_repo)
):
    await repo.replace_social_links(user.user_id, [s.model_dump(exclude={'link_id'}) for s in data])
    return {"status": "ok"}
