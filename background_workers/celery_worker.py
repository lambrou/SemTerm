import os
import sys
import traceback
from datetime import datetime

from bson import ObjectId
from celery import Celery
from background_workers import celeryconfig
from database.connection_pool import get_db_client
from pipelines.CaseSummaryPipeline import CaseSummaryPipeline

redis_url = 'redis://' + os.environ.get("REDIS_URL", "redis:6379") + '/0'
celery_app = Celery(__name__, include='background_workers.celery_worker', broker=redis_url, backend=redis_url)
celery_app.config_from_object(celeryconfig)


@celery_app.task(bind=True)
def summarize_case(self, case_data_dict, summary_id):
    client = get_db_client()
    db = client['generative_summarizer']
    result, pipeline, result = None, None, None
    try:
        pipeline = CaseSummaryPipeline(**case_data_dict)
    except Exception as e:
        self.update_state(state='FAILURE')
        result = db['case_summaries'].update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": {"status": "FAILED"}}
        )
        return {"error": f"Pipeline failed to initialize. {e}"}
    try:
        summary = pipeline.process()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.update_state(state='FAILURE')
        result = db['case_summaries'].update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": {"status": "FAILED"}}
        )
        return {
            "error": f"Pipeline failed to process. {e} {fname} {exc_tb.tb_lineno} {exc_type} {exc_obj}\n{traceback.format_exc()}"}
    try:
        result = db['case_summaries'].update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": {"summary": summary, "completed_date": datetime.now(), "status": "COMPLETED"}}
        )
    except Exception as e:
        self.update_state(state='FAILURE')
        result = db['case_summaries'].update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": {"status": "FAILED"}}
        )
        return {"error": f"Failed to insert summary. {e}"}
    if not result or not result.acknowledged:
        self.update_state(state='FAILURE')
        result = db['case_summaries'].update_one(
            {"_id": ObjectId(summary_id)},
            {"$set": {"status": "FAILED"}}
        )
        return {"error": "Generic Summary issue."}
    return str(summary_id)
