from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from autonomous_online_learner_tutor import learn_and_teach_anything
except ImportError:
    learn_and_teach_anything = None

router = APIRouter()


class TutorRequest(BaseModel):
    user_prompt: str


@router.post("/learn", response_model=Dict[str, Any])
async def trigger_tutor(request: TutorRequest):
    """
    Triggers the autonomous online learner tutor.
    In Phase 3, this will be migrated to a Celery background task.
    """
    if not learn_and_teach_anything:
        raise HTTPException(
            status_code=500, detail="autonomous_online_learner_tutor module not found"
        )

    try:
        response = learn_and_teach_anything(request.user_prompt)
        return {
            "status": "success",
            "message": "Tutor executed successfully",
            "response": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
