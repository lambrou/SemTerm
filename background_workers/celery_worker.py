from asgiref.sync import async_to_sync
from celery import Celery

from models.Summary import CaseSummary

celery_app = Celery(__name__, include='background_workers.celery_worker', broker="redis://localhost:6379/0",
                    config_source="background_workers.celeryconfig")


@celery_app.task
def summarize_case(case_data_dict):
    from main import app
    pipeline = create_case_summary_pipeline(case_data_dict)
    summary = pipeline.process()

    result = app.state.databasesync.summaries.insert_one(
        CaseSummary(case_data=case_data_dict, summary=summary).dict()
    )
    if not result.acknowledged:
        return {"error": "Failed to insert summary."}
    return {"result": str(result.inserted_id)}


def create_case_summary_pipeline(case_data_dict):
    from pipelines.CaseSummaryPipeline import CaseSummaryPipeline
    return CaseSummaryPipeline(**case_data_dict)
