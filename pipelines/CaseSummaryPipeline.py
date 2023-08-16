import json
from typing import List

import graphsignal
import trafilatura
from celery.contrib import rdb
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from pydantic import root_validator, ValidationError, BaseModel

from langchain_adapter.summaries.chains.SummaryChainFactory import SummaryChainFactory, SummaryInputType, \
    SummaryChainType
from preprocessing.IdentityHandler import IdentityHandler
from preprocessing.TokenHandler import TokenHandler
from settings.Settings import settings

graphsignal.configure(api_key=settings.graphsignal_api_key, deployment=settings.environment)


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
    org_id: str | None = None

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

    def preprocess(self, data, type):
        unwanted_keys = [
            'id', 'sponsor_partners_teams_id', 'owner_partners_teams_id', 'source', 'collaborator_partners_teams_ids',
            'type', 'claimed', 'created', 'customer', 'location', 'customerUser', 'name', 'email', 'phone', 'sponsor',
            'zipcode', 'site_name', 'first_name', 'last_name', 'sms_number', "c__d_case_priority", "c__d_status",
            "c__d_type", "c__industry", "c__resolution_type", "category", "member_industry", "case_assigned_to",
            "c_d_sources", "c__is_escalated", "owner_users_id", "c__tags", "c__articles", "c__owner_partner_team_id",
            "c__owner_partner_id", "location", "members_id", "members_locations_id", "members_users_id",
            "c__owner_partner_name", "c__owner_partner_team_name",
        ]
        data_str = ''
        if type == 'transcript':
            data.reverse()
            for i, message in enumerate(data, 1):
                if message:
                    data_str += f'\n---BEGIN MESSAGE {i}---\n'
                    if message['payload'] and 'email' in message['payload']:
                        email = message.get('payload').get('email').get('body') or message.get('text')
                        email = trafilatura.extract(email) or email
                        email = email.replace('\\n', '\n')
                        data_str += email
                    else:
                        data_str += message.get('text')
                    data_str += '\n---END OF MESSAGE---\n'

        elif type == 'metadata':
            metadata_cleaned = {k: v for k, v in data.items() if v and k not in unwanted_keys}
            data_str = str(metadata_cleaned)

        deidentified_data = self.identity_handler.deidentifier.deidentify(data_str)
        surrogated_data = self.identity_handler.surrogate(data_str, deidentified_data)
        return self.token_handler.split_by_token(surrogated_data.deidentified_text)

    def process(self):
        if not self.case_metadata and not self.case_transcript:
            return 'Not enough data for summary generation.'
        summarized_transcript = None
        summarized_metadata = None
        summarizer = self.summary_chain_factory.create(SummaryInputType.CASE, SummaryChainType.REFINE)
        final_summary_surrogated = None

        with graphsignal.start_trace('summary_pipeline'):
            graphsignal.set_context_tag('ORG_ID', self.org_id)
            if self.case_transcript and len(str(self.case_transcript)) > 20:
                split_transcript = self.preprocess(self.case_transcript, 'transcript')
                summarized_transcript = summarizer.run({"input_documents": split_transcript})

            if self.case_metadata and len(str(self.case_metadata)) > 20:
                split_metadata = self.preprocess(self.case_metadata, 'metadata')
                summarized_metadata = summarizer.run({"input_documents": split_metadata})

            if summarized_transcript and summarized_metadata:
                summary_summarizer = self.summary_chain_factory.create(SummaryInputType.SUMM, SummaryChainType.REFINE)
                summarized_transcript_doc = [Document(page_content=summarized_transcript)]
                final_summary_surrogated = summary_summarizer.run({
                    "input_documents": summarized_transcript_doc,
                    "internal_notes_summary": summarized_metadata
                })
            else:
                final_summary_surrogated = summarized_transcript if summarized_transcript else summarized_metadata

        reidentified_summary = self.identity_handler.reidentify(final_summary_surrogated)
        return reidentified_summary if final_summary_surrogated else 'Not enough data for summary generation.'


def is_email(x):
    return x.get('payload')
