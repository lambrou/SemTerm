import pytest
from unittest.mock import patch, ANY, MagicMock
from bson import ObjectId
from hypothesis import given, settings, Phase

from background_workers.celery_worker import summarize_case
from tests.utils.transcript_generator import TestDataGenerator


@patch("background_workers.celery_worker.get_db_client")
@patch("background_workers.celery_worker.CaseSummaryPipeline")
@patch("background_workers.celery_worker.celery_app")
class TestSummarizeCase:
    @settings(max_examples=1, phases=[Phase.explicit, Phase.reuse, Phase.generate])
    @given(
        case_transcript=TestDataGenerator.generate_transcript(),
    )
    def test_summarize_case_success(
        self,
        celery_app,
        mock_case_summary_pipeline,
        mock_get_db_client,
        case_transcript,
    ):
        celery_app.task.side_effect = lambda func: func.__get__(func, type(func))

        mock_pipeline_instance = mock_case_summary_pipeline.return_value
        mock_pipeline_instance.process.return_value = "Test Summary"

        summary_id = ObjectId()
        mock_db = MagicMock()
        mock_get_db_client.return_value = {"generative_summarizer": mock_db}

        result = summarize_case(
            case_data_dict={
                "case_transcript": case_transcript,
                "case_metadata": {"some_random_metadata": "random metadata"},
                "org_id": "1",
            },
            summary_id=str(summary_id),
        )

        mock_db["case_summaries"].update_one.assert_called_with(
            {"_id": summary_id},
            {
                "$set": {
                    "summary": "Test Summary",
                    "completed_date": ANY,
                    "status": "COMPLETED",
                }
            },
        )

        assert result == str(summary_id)

    @settings(max_examples=1, phases=[Phase.explicit, Phase.reuse, Phase.generate])
    @given(case_transcript=TestDataGenerator.generate_transcript())
    def test_summarize_case_db_connection_failure(
        self,
        celery_app,
        mock_case_summary_pipeline,
        mock_get_db_client,
        case_transcript,
    ):
        mock_get_db_client.side_effect = Exception("DB Connection Failure")

        summary_id = ObjectId()

        result = summarize_case.apply(
            args=({"case_transcript": case_transcript}, str(summary_id))
        ).get()

        assert result["error"] == "Database connection failed: DB Connection Failure"

    @settings(max_examples=1, phases=[Phase.explicit, Phase.reuse, Phase.generate])
    @given(case_transcript=TestDataGenerator.generate_transcript())
    def test_summarize_case_pipeline_init_failure(
        self,
        celery_app,
        mock_case_summary_pipeline,
        mock_get_db_client,
        case_transcript,
    ):
        mock_case_summary_pipeline.side_effect = Exception(
            "Pipeline Initialization Failure"
        )

        summary_id = ObjectId()
        mock_db = MagicMock()
        mock_get_db_client.return_value = {"generative_summarizer": mock_db}

        result = summarize_case.apply(
            args=({"case_transcript": case_transcript}, str(summary_id))
        ).get()

        assert (
            result["error"]
            == "Pipeline Initialization Error: Pipeline Initialization Failure"
        )

    @settings(max_examples=1, phases=[Phase.explicit, Phase.reuse, Phase.generate])
    @given(
        case_transcript=TestDataGenerator.generate_transcript(),
    )
    @pytest.mark.celery(result_backend=None)
    async def test_summarize_case_failure(
        self,
        celery_app,
        mock_case_summary_pipeline,
        mock_get_db_client,
        case_transcript,
    ):
        celery_app.task.side_effect = lambda func: func.__get__(func, type(func))

        mock_pipeline_instance = mock_case_summary_pipeline.return_value
        mock_pipeline_instance.process.side_effect = Exception("Expected failure")

        summary_id = ObjectId()
        mock_db = MagicMock()
        mock_get_db_client.return_value = {"generative_summarizer": mock_db}

        summarize_case.apply(
            args=(
                {
                    "case_transcript": case_transcript,
                    "case_metadata": {"some_random_metadata": "random metadata"},
                    "org_id": "1",
                },
                str(summary_id),
            )
        ).get()

        mock_db["case_summaries"].update_one.assert_called_with(
            {"_id": summary_id},
            {
                "$set": {
                    "status": "FAILED",
                }
            },
        )
