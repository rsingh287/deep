import os
import sys

from celery import Celery

# Add parent directory to path to allow importing existing modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from enterprise_app.core.config import settings

celery_app = Celery(
    "3d_buddy_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["enterprise_app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Configure periodic tasks (the actual autonomous loop!)
    beat_schedule={
        "autonomous_hft_arbitrage_every_5_mins": {
            "task": "enterprise_app.worker.tasks.run_hft_arbitrage",
            "schedule": 300.0,  # seconds
        },
        "autonomous_job_applier_every_hour": {
            "task": "enterprise_app.worker.tasks.run_job_applier",
            "schedule": 3600.0,  # seconds
        },
    },
)
