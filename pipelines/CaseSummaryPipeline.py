from typing import List

import trafilatura
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from pydantic import root_validator, ValidationError, BaseModel

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

    case_transcript: List[dict] | None = None
    case_metadata: dict | None = None
    token_handler = TokenHandler(llm_name='gpt-3.5-turbo')
    identity_handler = IdentityHandler()
    summary_chain_factory = SummaryChainFactory(llm=ChatOpenAI(model_name='gpt-3.5-turbo'))

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def validate_model(cls, values):
        if not values.get('case_metadata') and not values.get('case_transcript'):
            return ValidationError('Must have at least one of case_metadata or case_transcript')
        else:
            return values

    def preprocess(self, text):
        text_no_html = trafilatura.extract(text)
        if not text_no_html:
            text_no_html = text
        deidentified_metadata = self.identity_handler.deidentifier.deidentify(text_no_html)
        surrogated_metadata = self.identity_handler.surrogate(deidentified_metadata)
        return self.token_handler.split_by_token(surrogated_metadata.deidentified_text)

    def process(self):
        if not self.case_metadata and not self.case_transcript:
            return 'Not enough data for summary generation.'
        summarized_transcript = None
        summarized_metadata = None
        summarizer = self.summary_chain_factory.create(SummaryInputType.CASE, SummaryChainType.REFINE)
        final_summary_surrogated = None
        if self.case_transcript and len(str(self.case_transcript)) > 20:
            transcript_str = str(self.case_transcript)
            split_transcript = self.preprocess(transcript_str)
            summarized_transcript = summarizer.run({"input_documents": split_transcript})

        if self.case_metadata and len(str(self.case_metadata)) > 20:
            metadata_scrubbed = {k: v for k, v in self.case_metadata.items() if v}
            metadata_str = str(metadata_scrubbed)
            split_metadata = self.preprocess(metadata_str)
            summarized_metadata = summarizer.run({"input_documents": split_metadata})

        if summarized_transcript and summarized_metadata:
            summary_summarizer = self.summary_chain_factory.create(SummaryInputType.SUMM, SummaryChainType.REFINE)
            summarized_transcript_doc = [Document(page_content=summarized_transcript)]
            summarized_metadata_doc = [Document(page_content=summarized_metadata)]
            final_summary_surrogated = summary_summarizer.run({
                "input_documents": summarized_transcript_doc,
                "internal_notes_summary": summarized_metadata_doc
            })
        else:
            final_summary_surrogated = summarized_transcript if summarized_transcript else summarized_metadata

        reidentified_summary = self.identity_handler.reidentify(final_summary_surrogated)
        return reidentified_summary if final_summary_surrogated else 'Not enough data for summary generation.'
