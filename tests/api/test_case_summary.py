import pytest
from hypothesis import given, strategies as strategy
from tests.utils.TestTokenHandler import TestTokenHandler
from unittest.mock import patch, MagicMock
from pipelines.CaseSummaryPipeline import CaseSummaryPipeline
from background_workers.celery_worker import summarize_case


class TestSummarizeCase:
    @given(
        n_metadata_tokens=strategy.integers(min_value=0, max_value=20000),
        n_transcript_tokens=strategy.integers(min_value=0, max_value=20000)
    )
    @pytest.mark.anyio
    async def test_summarize_case(self, test_client, n_metadata_tokens: int, n_transcript_tokens: int):
        mock_pipeline = MagicMock(spec=CaseSummaryPipeline)
        mock_pipeline.process.return_value = 'mock_summary'
        with patch('background_workers.celery_worker.create_case_summary_pipeline', return_value=mock_pipeline):
            token_handler = TestTokenHandler()
            case_metadata = token_handler.generate_nonsensical_tokens(n_metadata_tokens)
            case_transcript = token_handler.generate_nonsensical_tokens(n_transcript_tokens)
            if case_metadata:
                case_metadata = {"idr_isq": " ".join(case_metadata)}
            response = await test_client.post(
                "/summarize/summarize_case",
                json={
                    "case_metadata": case_metadata,
                    "case_transcript": case_transcript,
                    "case_id": "1234"
                }
            )
            if not n_metadata_tokens and not n_transcript_tokens:
                assert response.status_code == 422
            else:
                assert response.status_code == 202
                task_id = response.json()["task_id"]
                assert task_id
                assert isinstance(task_id, str)
                assert "message" in response.json()
                assert "task_id" in response.json()
