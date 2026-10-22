from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Import from legacy engine
try:
    import autonomous_job_applier
except ImportError:
    autonomous_job_applier = None

router = APIRouter()


class JobProfileUpdate(BaseModel):
    name: str
    email: str
    phone: str
    skills: str
    experience: str


class AutoApplyRequest(BaseModel):
    job_title: str
    company: str
    job_url: str = "https://remoteok.com"


@router.get("/profile", response_model=Dict[str, Any])
async def get_profile():
    if not autonomous_job_applier:
        raise HTTPException(
            status_code=500, detail="autonomous_job_applier module not found"
        )
    profile = autonomous_job_applier.get_user_job_profile()
    if profile:
        return dict(profile)
    return {"message": "Profile not found"}


@router.put("/profile", response_model=Dict[str, Any])
async def update_profile(profile: JobProfileUpdate):
    if not autonomous_job_applier:
        raise HTTPException(
            status_code=500, detail="autonomous_job_applier module not found"
        )
    autonomous_job_applier.update_user_job_profile(
        profile.name, profile.email, profile.phone, profile.skills, profile.experience
    )
    return {"status": "success", "message": "Profile updated successfully"}


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_jobs(
    query: str = Query(default="IT Support Specialist"),
    location: str = Query(default="Ontario"),
    limit: int = Query(default=6),
):
    if not autonomous_job_applier:
        raise HTTPException(
            status_code=500, detail="autonomous_job_applier module not found"
        )
    try:
        jobs = autonomous_job_applier.search_live_it_jobs(
            query=query, location=location, limit=limit
        )
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply", response_model=Dict[str, Any])
async def auto_apply(request: AutoApplyRequest):
    """
    Triggers the autonomous job applier.
    In Phase 3, this will be migrated to a Celery background task.
    """
    if not autonomous_job_applier:
        raise HTTPException(
            status_code=500, detail="autonomous_job_applier module not found"
        )
    try:
        result = autonomous_job_applier.auto_apply_to_job(
            job_title=request.job_title,
            company=request.company,
            job_url=request.job_url,
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_history():
    if not autonomous_job_applier:
        raise HTTPException(
            status_code=500, detail="autonomous_job_applier module not found"
        )
    try:
        history = autonomous_job_applier.get_job_application_history()
        return [dict(h) for h in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
