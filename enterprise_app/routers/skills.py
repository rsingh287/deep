from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enterprise_app.core.database import get_db
from enterprise_app.core.logging import logger
from enterprise_app.models.skill import AgentSkill

router = APIRouter()


class SkillResponse(BaseModel):
    id: str
    name: str
    category: str
    plugin: Optional[str] = None
    scope: Optional[str] = "Global"
    description: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    category: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """Retrieve all skills, optionally filtered by category."""
    query = select(AgentSkill)
    if category:
        query = query.where(AgentSkill.category == category)

    result = await db.execute(query)
    skills = result.scalars().all()
    logger.info(f"Retrieved {len(skills)} skills")
    return skills


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific skill."""
    query = select(AgentSkill).where(AgentSkill.id == skill_id)
    result = await db.execute(query)
    skill = result.scalar_one_or_none()

    if not skill:
        logger.warning(f"Skill not found: {skill_id}")
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill
