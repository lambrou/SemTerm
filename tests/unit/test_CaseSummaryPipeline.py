from unittest.mock import MagicMock

from _pytest.python_api import raises
from hypothesis import given, settings
import hypothesis.strategies as strategy
from pydantic import ValidationError

from pipelines.CaseSummaryPipeline import CaseSummaryPipeline
from tests.utils.transcript_generator import TestDataGenerator


class TestCaseSummaryPipeline:
    @settings(max_examples=1)
    @given(
        random_metadata=strategy.from_regex(
            "^(?=.*[a-zA-Z])[\w\s\.,!?]*$", fullmatch=True
        ),
        case_transcript=TestDataGenerator.generate_transcript(),
    )
    def test_pipeline(self, random_metadata, case_transcript):
        pipeline = CaseSummaryPipeline(
            case_transcript=case_transcript,
            case_metadata={"some_random_metadata": random_metadata},
            org_id="1",
        )
        mock_summary_chain = MagicMock()
        mock_summary_chain.run = MagicMock(return_value="mocked summary text")
        pipeline.summary_chain_factory = MagicMock()
        pipeline.summary_chain_factory.create = MagicMock(
            return_value=mock_summary_chain
        )
        result = pipeline.process()
        assert isinstance(result, str), "The output must be a string."
        for key in pipeline.identity_handler.identity_cache.keys():
            assert (
                key not in result
            ), f"The key {key} should not appear in the reidentified text."

    def test_no_metadata_no_transcript(self):
        with raises(ValidationError):
            CaseSummaryPipeline(case_transcript=None, case_metadata=None)

    @settings(max_examples=1)
    @given(
        random_metadata=strategy.from_regex(
            "^(?=.*[a-zA-Z])[\w\s\.,!?]*$", fullmatch=True
        ),
    )
    def test_only_metadata(self, random_metadata):
        pipeline = CaseSummaryPipeline(
            case_metadata={"text": random_metadata}, org_id="1"
        )
        result = pipeline.process()
        assert isinstance(result, str), "The output must be a string."

    @settings(max_examples=1)
    @given(
        case_transcript=TestDataGenerator.generate_transcript(),
    )
    def test_only_transcript(self, case_transcript):
        pipeline = CaseSummaryPipeline(
            case_transcript=case_transcript or [{"some text": "more text"}],
            case_metadata=None,
            org_id="1",
        )
        result = pipeline.process()
        assert isinstance(result, str), "The output must be a string."

    def test_too_short_for_summary(self, org_id=1):
        pipeline = CaseSummaryPipeline(
            case_transcript=[{"some_key": "some_value"}],
            case_metadata={"key": "value"},
            org_id=str(org_id),
        )
        assert pipeline.process() == "Not enough data for summary generation."

    def test_preprocess(self):
        pipeline = CaseSummaryPipeline(
            case_transcript=[
                {"text": "Some text", "payload": {"email": {"body": "email body"}}}
            ],
            case_metadata={"key": "value"},
        )

        processed_transcript = pipeline.preprocess(
            pipeline.case_transcript, "transcript"
        )
        processed_metadata = pipeline.preprocess(pipeline.case_metadata, "metadata")

        assert isinstance(processed_transcript, list)
        assert isinstance(processed_metadata, list)
