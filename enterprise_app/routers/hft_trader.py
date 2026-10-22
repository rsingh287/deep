from typing import Any, Dict

from fastapi import APIRouter, HTTPException

try:
    from apex_hft_arbitrage_engine import (
        ApexHFTArbitrageEngine,
        format_apex_sovereign_report,
    )
except ImportError:
    ApexHFTArbitrageEngine = None
    format_apex_sovereign_report = None

router = APIRouter()


@router.post("/execute", response_model=Dict[str, Any])
async def execute_hft_arbitrage():
    """
    Executes the Apex HFT Arbitrage Engine.
    In Phase 3, this will be migrated to a Celery background task.
    """
    if not ApexHFTArbitrageEngine:
        raise HTTPException(
            status_code=500, detail="apex_hft_arbitrage_engine module not found"
        )

    try:
        engine = ApexHFTArbitrageEngine()
        opportunities = engine.execute_apex_sovereign_arbitrage()
        report = format_apex_sovereign_report(
            opportunities, None
        )  # Skipping quantum cov for simplicity in API
        return {
            "status": "success",
            "message": "HFT Arbitrage executed successfully",
            "opportunities_found": len(opportunities),
            "report_preview": (
                report[:200] + "..." if report and len(report) > 200 else report
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
