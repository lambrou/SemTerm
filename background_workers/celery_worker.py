import os
from datetime import datetime

from bson import ObjectId
from celery import Celery
from pymongo.errors import PyMongoError

from background_workers import celeryconfig
from database.connection_pool import get_db_client
from pipelines.CaseSummaryPipeline import CaseSummaryPipeline

redis_url = 'redis://' + os.environ.get("REDIS_URL", "redis:6379") + '/0'
celery_app = Celery(__name__, include='background_workers.celery_worker', broker=redis_url, backend=redis_url)
celery_app.config_from_object(celeryconfig)


def update_failure_status(db, summary_id):
    try:
        return db["case_summaries"].update_one(
            {"_id": ObjectId(summary_id)}, {"$set": {"status": "FAILED"}}
        )
    except PyMongoError:
        raise


def update_success_status(db, summary_id, summary):
    try:
        return db["case_summaries"].update_one(
            {"_id": ObjectId(summary_id)},
            {
                "$set": {
                    "summary": summary,
                    "completed_date": datetime.now(),
                    "status": "COMPLETED",
                }
            },
        )
    except PyMongoError:
        raise


@celery_app.task(bind=True)
def summarize_case(self, case_data_dict, summary_id):
    try:
        client = get_db_client()
        db = client["generative_summarizer"]
    except Exception as e:
        self.update_state(state="FAILURE")
        return {"error": f"Database connection failed: {e}"}

    try:
        pipeline = CaseSummaryPipeline(**case_data_dict)
    except Exception as e:
        self.update_state(state="FAILURE")
        update_failure_status(db, summary_id)
        return {"error": f"Pipeline Initialization Error: {e}"}

    try:
        summary = pipeline.process()
    except Exception as e:
        self.update_state(state="FAILURE")
        update_failure_status(db, summary_id)
        return {"error": f"Pipeline Processing Error: {e}"}

    try:
        result = update_success_status(db, summary_id, summary)
    except Exception as e:
        self.update_state(state="FAILURE")
        update_failure_status(db, summary_id)
        return {"error": f"Failed to update summary in database: {e}"}

    if not result or not result.acknowledged:
        self.update_state(state="FAILURE")
        update_failure_status(db, summary_id)
        return {"error": "Generic Summary issue."}

    return str(summary_id)
