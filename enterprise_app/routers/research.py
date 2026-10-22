from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from autonomous_research_powerbi_engine import generate_research_and_powerbi_report
except ImportError:
    generate_research_and_powerbi_report = None

router = APIRouter()


class ResearchRequest(BaseModel):
    topic_or_dataset_prompt: str


@router.post("/generate", response_model=Dict[str, Any])
async def trigger_research(request: ResearchRequest):
    """
    Triggers the autonomous research and PowerBI engine.
    In Phase 3, this will be migrated to a Celery background task.
    """
    if not generate_research_and_powerbi_report:
        raise HTTPException(
            status_code=500,
            detail="autonomous_research_powerbi_engine module not found",
        )

    try:
        report = generate_research_and_powerbi_report(request.topic_or_dataset_prompt)
        return {
            "status": "success",
            "message": "Research executed successfully",
            "report_preview": (
                report[:200] + "..." if report and len(report) > 200 else report
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
