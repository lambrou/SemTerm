from enum import Enum
from typing import Optional, List

from langchain import PromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import RefineDocumentsChain
from pydantic import BaseModel

from langchain_adapter.summaries.prompts.CasePrompt import (
    summarize_case_prompt_template,
    summarize_case_refine_template,
)
from langchain_adapter.summaries.prompts.CombineSummaries import (
    summarize_summaries_prompt_template,
    summarize_summaries_refine_template,
)


class SummaryChainType(str, Enum):
    REFINE = "refine"
    REDUCE = "map_reduce"
    STUFF = "stuff"


class SummaryInputType(str, Enum):
    CASE = "case"
    CUSTOMER = "customer"
    ORG = "org"
    SUMM = "summary"


class SummaryChainFactory(BaseModel):
    """
    Factory to create a Langchain Chain for Summarization.
    Usage:
        summarizer_factory = SummaryChainFactory(llm=self.model)
        case_summarizer = summarizer_factory.create(SummaryInputType.CASE, SummaryChainType.REFINE)
        case_summarizer.run({"input_documents": case_transcript})
    """

    llm: BaseLanguageModel
    """The language model to use for generation."""

    document_variable_name: str = "text"
    """The variable name to put the documents in."""
    initial_response_name: str = "existing_summary"
    """The variable name to format the initial response in when refining."""
    prompt_template: Optional[str] = None
    """The template to use for the prompt. Changed based on input and chain type."""
    refine_template: Optional[str] = None
    """The template to use for the refine prompt, if any. Optional. Changed based on input and chain type."""
    extra_input_variables: List[str] = []

    def create(self, input_type: SummaryInputType, chain_type: SummaryChainType):
        """
        Create a chain for summarization.
            :param input_type: The type of input to run through summarization. Must be one of SummaryInputType.
            :param chain_type: The type of Summary Chain to create. Must be one of SummaryChainType.
            :return: A Langchain Chain designed for summarization.
        """
        if chain_type == SummaryChainType.REFINE:
            if input_type == SummaryInputType.SUMM:
                self.extra_input_variables += ["internal_notes_summary"]
                self.prompt_template = summarize_summaries_prompt_template
                self.refine_template = summarize_summaries_refine_template
            elif input_type == SummaryInputType.CASE:
                self.prompt_template = summarize_case_prompt_template
                self.refine_template = summarize_case_refine_template
            else:
                raise NotImplementedError(f"Input type {input_type} not implemented.")
            return self._create_refine_chain()
        else:
            raise NotImplementedError(f"Chain type {chain_type} not implemented.")

    def _create_refine_chain(self):
        question_prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=[self.document_variable_name, *self.extra_input_variables],
        )
        refine_prompt = PromptTemplate(
            input_variables=[
                self.initial_response_name,
                self.document_variable_name,
                *self.extra_input_variables,
            ],
            template=self.refine_template,
        )
        initial_llm_chain = LLMChain(
            llm=self.llm, prompt=question_prompt, verbose=False
        )
        refine_llm_chain = LLMChain(llm=self.llm, prompt=refine_prompt, verbose=False)
        return RefineDocumentsChain(
            initial_llm_chain=initial_llm_chain,
            refine_llm_chain=refine_llm_chain,
            document_variable_name=self.document_variable_name,
            initial_response_name=self.initial_response_name,
        )
