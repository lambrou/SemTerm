import pytest
from hypothesis import given, strategies as strategy, settings, Phase

from tests.utils.TestTokenHandler import TestTokenHandler
from unittest.mock import patch, MagicMock
from pipelines.CaseSummaryPipeline import CaseSummaryPipeline
from tests.utils.transcript_generator import TestDataGenerator


class TestSummarizeCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.pipeline = CaseSummaryPipeline(
            case_metadata={"some_key": "some_value"},
            case_transcript=[
                {
                    "payload": {"email": {"body": "<html>Hello</html>"}},
                    "text": "some text",
                }
            ],
        )

    @settings(max_examples=5, phases=[Phase.explicit, Phase.reuse, Phase.generate])
    @given(
        n_metadata_tokens=strategy.integers(min_value=0, max_value=20000),
        n_transcript_tokens=strategy.integers(min_value=0, max_value=20000),
        case_transcript=TestDataGenerator.generate_transcript(),
    )
    @pytest.mark.anyio
    async def test_summarize_case(
        self,
        test_client,
        n_metadata_tokens: int,
        n_transcript_tokens: int,
        case_transcript: dict,
    ):
        mock_pipeline = MagicMock(spec=CaseSummaryPipeline)
        mock_pipeline.process.return_value = "mock_summary"
        with patch(
            "background_workers.celery_worker.CaseSummaryPipeline",
            return_value=mock_pipeline,
        ):
            token_handler = TestTokenHandler()
            case_metadata = token_handler.generate_nonsensical_tokens(n_metadata_tokens)
            if case_metadata:
                case_metadata = {"idr_isq": " ".join(case_metadata)}
            response = await test_client.post(
                "/case",
                json={
                    "case_metadata": case_metadata,
                    "case_transcript": case_transcript,
                    "case_id": "1234",
                    "org_id": "5678",
                },
            )
            if not n_metadata_tokens and not n_transcript_tokens:
                assert response.status_code == 422
            else:
                assert "message" in response.json()
                assert "summary_id" in response.json()
                print(response.json())
                assert response.status_code == 202
                summary_id = response.json()["summary_id"]
                assert summary_id
                assert isinstance(summary_id, str)

    def test_preprocess_transcript(self):
        self.pipeline.case_metadata = {"some_key": "Hello I'm John Smith."}
        self.pipeline.case_transcript = [
            {
                "payload": {
                    "email": {
                        "body": "<html>Hello I'm John Smith. How are you today?</html>"
                    }
                },
                "text": "Hello I'm John Smith.",
            }
        ]

        transcript_result = self.pipeline.preprocess(
            self.pipeline.case_transcript, "transcript"
        )

        assert isinstance(transcript_result, list)
        assert "John Smith" not in transcript_result

    def test_preprocess_metadata(self):
        data = {"some_key": "some_value", "unwanted_key": "unwanted_value"}
        data_type = "metadata"
        result = self.pipeline.preprocess(data, data_type)
        assert isinstance(result, list), "The output must be a string."

    def test_process_no_data(self):
        self.pipeline.case_metadata = None
        self.pipeline.case_transcript = None
        result = self.pipeline.process()
        assert result == "Not enough data for summary generation."

    def test_process_with_both(self):
        self.pipeline.case_metadata = {"some_key": "some_value"}
        self.pipeline.case_transcript = [
            {"payload": {"email": {"body": "<html>Hello</html>"}}, "text": "some text"}
        ]
        result = self.pipeline.process()

        assert isinstance(result, str), "The output must be a string."
