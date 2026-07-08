import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
import redis.asyncio as redis
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from orchestration.api.config import get_settings
from orchestration.db.models import (
    UserProfile,
    UserExperience,
    UserEducation,
    UserProject,
    UserCertification,
    UserSkill,
    UserLanguage,
    UserAchievement,
    UserSocialLink,
)

logger = logging.getLogger(__name__)

class PostgresProfileRepository:
    """Repository for managing user profiles and related entities."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()

    async def _get_redis(self):
        return redis.Redis.from_url(self.settings.redis.redis_url, decode_responses=True)

    async def get_profile(self, user_id: UUID) -> Optional[UserProfile]:
        stmt = (
            select(UserProfile)
            .where(UserProfile.user_id == user_id)
            .options(
                selectinload(UserProfile.experiences),
                selectinload(UserProfile.education),
                selectinload(UserProfile.projects),
                selectinload(UserProfile.certifications),
                selectinload(UserProfile.skills),
                selectinload(UserProfile.languages),
                selectinload(UserProfile.achievements),
                selectinload(UserProfile.social_links),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_public_profile(self, username: str) -> Optional[UserProfile]:
        stmt = (
            select(UserProfile)
            .where(and_(UserProfile.username == username, UserProfile.is_public == True))
            .options(
                selectinload(UserProfile.experiences),
                selectinload(UserProfile.education),
                selectinload(UserProfile.projects),
                selectinload(UserProfile.certifications),
                selectinload(UserProfile.skills),
                selectinload(UserProfile.languages),
                selectinload(UserProfile.achievements),
                selectinload(UserProfile.social_links),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_username_available(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if a username is available.
        Uses Redis Bloom Filter for fast path rejection, then falls back to SQL query.
        """
        redis_client = await self._get_redis()
        bf_key = "jh:bf:usernames"
        try:
            # Check Bloom filter first
            # bf() returns a client for Bloom Filter commands if redis-py supports it.
            # If not using redis-py > 4.0, might need to use execute_command.
            exists_in_bf = await redis_client.execute_command("BF.EXISTS", bf_key, username)
            if not exists_in_bf:
                # Definitely not taken
                return True
        except redis.RedisError as e:
            logger.warning(f"Redis Bloom Filter error during username check: {e}")
            # Fall through to DB check
        finally:
            await redis_client.aclose()

        # DB check (source of truth)
        stmt = select(UserProfile.user_id).where(UserProfile.username == username)
        if exclude_user_id:
            stmt = stmt.where(UserProfile.user_id != exclude_user_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is None

    async def upsert_profile(self, user_id: UUID, data: dict) -> UserProfile:
        """Upsert core profile identity data."""
        # Ensure username availability if provided
        new_username = data.get("username")
        if new_username:
            is_available = await self.check_username_available(new_username, exclude_user_id=user_id)
            if not is_available:
                raise ValueError("Username is already taken")

        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()

        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **data)
            self.session.add(profile)
            
        await self.session.flush()

        if new_username:
            redis_client = await self._get_redis()
            try:
                await redis_client.execute_command("BF.ADD", "jh:bf:usernames", new_username)
            except redis.RedisError as e:
                logger.warning(f"Failed to add username to Bloom filter: {e}")
            finally:
                await redis_client.aclose()

        return profile

    async def add_experience(self, user_id: UUID, data: dict) -> UserExperience:
        exp = UserExperience(user_id=user_id, **data)
        self.session.add(exp)
        await self.session.flush()
        return exp

    async def update_experience(self, user_id: UUID, exp_id: UUID, data: dict) -> Optional[UserExperience]:
        stmt = select(UserExperience).where(and_(UserExperience.user_id == user_id, UserExperience.exp_id == exp_id))
        result = await self.session.execute(stmt)
        exp = result.scalar_one_or_none()
        if not exp:
            return None
        for k, v in data.items():
            setattr(exp, k, v)
        await self.session.flush()
        return exp

    async def delete_experience(self, user_id: UUID, exp_id: UUID) -> bool:
        stmt = delete(UserExperience).where(and_(UserExperience.user_id == user_id, UserExperience.exp_id == exp_id))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def add_education(self, user_id: UUID, data: dict) -> UserEducation:
        edu = UserEducation(user_id=user_id, **data)
        self.session.add(edu)
        await self.session.flush()
        return edu

    async def update_education(self, user_id: UUID, edu_id: UUID, data: dict) -> Optional[UserEducation]:
        stmt = select(UserEducation).where(and_(UserEducation.user_id == user_id, UserEducation.edu_id == edu_id))
        result = await self.session.execute(stmt)
        edu = result.scalar_one_or_none()
        if not edu:
            return None
        for k, v in data.items():
            setattr(edu, k, v)
        await self.session.flush()
        return edu

    async def delete_education(self, user_id: UUID, edu_id: UUID) -> bool:
        stmt = delete(UserEducation).where(and_(UserEducation.user_id == user_id, UserEducation.edu_id == edu_id))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def add_project(self, user_id: UUID, data: dict) -> UserProject:
        proj = UserProject(user_id=user_id, **data)
        self.session.add(proj)
        await self.session.flush()
        return proj

    async def update_project(self, user_id: UUID, proj_id: UUID, data: dict) -> Optional[UserProject]:
        stmt = select(UserProject).where(and_(UserProject.user_id == user_id, UserProject.proj_id == proj_id))
        result = await self.session.execute(stmt)
        proj = result.scalar_one_or_none()
        if not proj:
            return None
        for k, v in data.items():
            setattr(proj, k, v)
        await self.session.flush()
        return proj

    async def delete_project(self, user_id: UUID, proj_id: UUID) -> bool:
        stmt = delete(UserProject).where(and_(UserProject.user_id == user_id, UserProject.proj_id == proj_id))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def replace_skills(self, user_id: UUID, skills_list: List[dict]):
        stmt = delete(UserSkill).where(UserSkill.user_id == user_id)
        await self.session.execute(stmt)
        if skills_list:
            objects = [UserSkill(user_id=user_id, **skill) for skill in skills_list]
            self.session.add_all(objects)
        await self.session.flush()

    async def replace_certifications(self, user_id: UUID, certs_list: List[dict]):
        stmt = delete(UserCertification).where(UserCertification.user_id == user_id)
        await self.session.execute(stmt)
        if certs_list:
            objects = [UserCertification(user_id=user_id, **cert) for cert in certs_list]
            self.session.add_all(objects)
        await self.session.flush()

    async def replace_languages(self, user_id: UUID, langs_list: List[dict]):
        stmt = delete(UserLanguage).where(UserLanguage.user_id == user_id)
        await self.session.execute(stmt)
        if langs_list:
            objects = [UserLanguage(user_id=user_id, **lang) for lang in langs_list]
            self.session.add_all(objects)
        await self.session.flush()

    async def replace_achievements(self, user_id: UUID, achs_list: List[dict]):
        stmt = delete(UserAchievement).where(UserAchievement.user_id == user_id)
        await self.session.execute(stmt)
        if achs_list:
            objects = [UserAchievement(user_id=user_id, **ach) for ach in achs_list]
            self.session.add_all(objects)
        await self.session.flush()

    async def replace_social_links(self, user_id: UUID, links_list: List[dict]):
        stmt = delete(UserSocialLink).where(UserSocialLink.user_id == user_id)
        await self.session.execute(stmt)
        if links_list:
            objects = [UserSocialLink(user_id=user_id, **link) for link in links_list]
            self.session.add_all(objects)
        await self.session.flush()
