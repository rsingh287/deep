from typing import Any, Dict

from fastapi import APIRouter, HTTPException

# Import from legacy engine
try:
    import autonomous_ml_benchmark_engine
except ImportError:
    autonomous_ml_benchmark_engine = None

router = APIRouter()


@router.post("/benchmark", response_model=Dict[str, Any])
async def trigger_ml_benchmark():
    """
    Triggers the autonomous ML benchmark suite.
    In Phase 3, this will be migrated to a Celery background task.
    """
    if not autonomous_ml_benchmark_engine:
        raise HTTPException(
            status_code=500, detail="autonomous_ml_benchmark_engine module not found"
        )

    try:
        # Note: This is currently a blocking call.
        # In Phase 3 with Celery, we will dispatch this asynchronously.
        report_md = autonomous_ml_benchmark_engine.execute_complete_ml_benchmark()
        return {
            "status": "success",
            "message": "ML Benchmark executed successfully",
            "report_preview": (
                report_md[:200] + "..." if len(report_md) > 200 else report_md
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
