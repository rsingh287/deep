import os
import sys

from fastapi import FastAPI

# Add parent directory to path to allow importing existing legacy modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .core.config import settings
from .core.logging import logger
from .routers import hft_trader, job_application, ml_benchmark, research, skills, tutor

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise API for 3D Buddy Autonomous System",
)

# Include routers
app.include_router(
    ml_benchmark.router, prefix=f"{settings.API_V1_STR}/ml", tags=["ML Benchmarking"]
)
app.include_router(
    job_application.router,
    prefix=f"{settings.API_V1_STR}/jobs",
    tags=["Job Applications"],
)
app.include_router(
    hft_trader.router, prefix=f"{settings.API_V1_STR}/hft", tags=["HFT Trading"]
)
app.include_router(
    tutor.router, prefix=f"{settings.API_V1_STR}/tutor", tags=["Autonomous Tutor"]
)
app.include_router(
    research.router, prefix=f"{settings.API_V1_STR}/research", tags=["Research Engine"]
)
app.include_router(
    skills.router, prefix=f"{settings.API_V1_STR}/skills", tags=["Skills"]
)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")


@app.get("/")
def read_root():
    logger.debug("Health check endpoint hit")
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "online"}
