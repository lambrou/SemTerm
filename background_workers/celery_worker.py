import os
import sys

from celery import Celery
from pymongo import MongoClient

from background_workers import celeryconfig
from database.connection_pool import get_db_client
from models.Summary import CaseSummary
from pipelines.CaseSummaryPipeline import CaseSummaryPipeline
from settings.Settings import settings

celery_app = Celery(__name__, include='background_workers.celery_worker', broker="redis://redis:6379/0",
                    backend="redis://redis:6379/0")
celery_app.config_from_object(celeryconfig)


@celery_app.task(bind=True)
def summarize_case(self, case_data_dict):
    client = get_db_client()
    db = client['generative_summarizer']
    result, pipeline, result = None, None, None
    try:
        pipeline = CaseSummaryPipeline(**case_data_dict)
    except Exception as e:
        self.update_state(state='FAILURE')
        return {"error": f"Pipeline failed to initialize. {e}"}
    try:
        summary = pipeline.process()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.update_state(state='FAILURE')
        return {"error": f"Pipeline failed to process. {e} {fname} {exc_tb.tb_lineno} {exc_type} {exc_obj}"}
    try:
        result = db['case_summaries'].insert_one(CaseSummary(case_data=case_data_dict, summary=summary).dict())
    except Exception as e:
        self.update_state(state='FAILURE')
        return {"error": f"Failed to insert summary. {e}"}
    if not result or not result.acknowledged:
        self.update_state(state='FAILURE')
        return {"error": "Generic Summary issue."}
    return str(result.inserted_id)
