from celery.utils.log import get_task_logger

from .celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def run_hft_arbitrage(self):
    """
    Background task to execute HFT Arbitrage continuously.
    """
    try:
        from apex_hft_arbitrage_engine import ApexHFTArbitrageEngine

        logger.info("Starting autonomous HFT Arbitrage execution...")
        engine = ApexHFTArbitrageEngine()
        opportunities = engine.execute_apex_sovereign_arbitrage()
        logger.info(f"HFT Arbitrage found {len(opportunities)} opportunities.")

        # Save to DB or notify in real-world scenario
        return {"status": "success", "opportunities": len(opportunities)}
    except ImportError:
        logger.error(
            "Could not import ApexHFTArbitrageEngine. Is the legacy module accessible?"
        )
        return {"status": "error", "message": "ImportError"}
    except Exception as e:
        logger.error(f"Error in HFT Arbitrage: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def run_job_applier(self):
    """
    Background task to autonomously search and apply for jobs.
    """
    try:
        import autonomous_job_applier

        logger.info("Starting autonomous Job Application execution...")
        jobs = autonomous_job_applier.search_live_it_jobs(limit=1)
        if jobs:
            job = jobs[0]
            result = autonomous_job_applier.auto_apply_to_job(
                job["title"], job["company"]
            )
            logger.info(
                f"Applied to {job['title']} at {job['company']}. Result: {result}"
            )
            return {"status": "success", "job": job["title"]}
        return {"status": "skipped", "message": "No new jobs found"}
    except ImportError:
        logger.error("Could not import autonomous_job_applier.")
        return {"status": "error", "message": "ImportError"}
    except Exception as e:
        logger.error(f"Error in Job Applier: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def run_ml_benchmark(self):
    """
    Background task for ML benchmarking.
    """
    try:
        import autonomous_ml_benchmark_engine

        logger.info("Starting autonomous ML Benchmark...")
        report = autonomous_ml_benchmark_engine.execute_complete_ml_benchmark()
        logger.info("ML Benchmark completed.")
        return {"status": "success", "report_length": len(report)}
    except ImportError:
        logger.error("Could not import autonomous_ml_benchmark_engine.")
        return {"status": "error"}
    except Exception as e:
        logger.error(f"Error in ML Benchmark: {e}")
        return {"status": "error"}
