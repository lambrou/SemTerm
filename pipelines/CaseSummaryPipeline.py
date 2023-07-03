from typing import Optional, List

from pydantic import root_validator, ValidationError, BaseModel, Field

from langchain_adapter.summaries.chains.SummaryChainFactory import SummaryChainFactory, SummaryInputType, \
    SummaryChainType
from preprocessing.IdentityHandler import IdentityHandler
from preprocessing.TokenHandler import TokenHandler


class CaseSummaryPipeline(BaseModel):
    """
    Pipeline for summarizing a case. Need at least one of case_metadata or case_transcript
    The default identity handler is used.
    1. Split data
    2. Deidentify data
    3. Surrogate data
    4. Summarize data
    5. Reidentify data
    """

    case_transcript: List[str] | None = None
    case_metadata: dict | None = None
    token_handler = TokenHandler
    identity_handler = IdentityHandler
    summary_chain_factory = SummaryChainFactory

    @root_validator
    def validate_model(cls, values):
        if not values.get('case_metadata') and not values.get('case_transcript'):
            return ValidationError('Must have at least one of case_metadata or case_transcript')
        else:
            return values

    def preprocess(self, text):
        deidentified_metadata = self.identity_handler.deidentifier.deidentify(text)
        surrogated_metadata = self.identity_handler.surrogate(deidentified_metadata)
        return self.token_handler.split_by_token(surrogated_metadata.deidentified_text)

    def process(self):
        summarized_transcript = None
        summarized_metadata = None
        summarizer = self.summary_chain_factory.create(SummaryInputType.CASE, SummaryChainType.REFINE)

        if self.case_transcript:
            split_transcript = self.preprocess(self.case_transcript)
            summarized_transcript = summarizer.run({"input_documents": split_transcript})

        if self.case_metadata:
            split_metadata = self.preprocess(str(self.case_metadata))
            summarized_metadata = summarizer.run({"input_documents": split_metadata})

        if summarized_transcript and summarized_metadata:
            final_summary_surrogated = summarizer.run({
                "input_documents": summarized_transcript,
                "internal_notes_summary": summarized_metadata
            })
        else:
            final_summary_surrogated = summarized_transcript if summarized_transcript else summarized_metadata

        return self.identity_handler.reidentify(final_summary_surrogated)
