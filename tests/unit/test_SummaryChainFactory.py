from hypothesis import given, strategies as st
import pytest
from unittest.mock import patch

from langchain.chat_models import ChatOpenAI

from langchain_adapter.summaries.chains.SummaryChainFactory import (
    SummaryChainFactory,
    SummaryInputType,
    SummaryChainType,
)

input_type_strategy = st.sampled_from([SummaryInputType.SUMM, SummaryInputType.CASE])
chain_type_strategy = st.sampled_from([SummaryChainType.REFINE])


@given(input_type=input_type_strategy, chain_type=chain_type_strategy)
@patch("langchain_adapter.summaries.chains.SummaryChainFactory.RefineDocumentsChain")
@patch("langchain_adapter.summaries.chains.SummaryChainFactory.PromptTemplate")
@patch("langchain_adapter.summaries.chains.SummaryChainFactory.LLMChain")
def test_create(
    mock_llm_chain,
    mock_prompt_template,
    mock_refine_documents_chain,
    input_type,
    chain_type,
):
    llm = ChatOpenAI()
    factory = SummaryChainFactory(
        llm=llm,
        document_variable_name="text",
        initial_response_name="existing_summary",
        extra_input_variables=[],
    )

    mock_prompt_template.return_value = "mocked_prompt"
    mock_llm_chain.return_value = "mocked_llm_chain"
    mock_refine_documents_chain.return_value = "mocked_refine_documents_chain"

    if chain_type == SummaryChainType.REFINE:
        if input_type not in [SummaryInputType.SUMM, SummaryInputType.CASE]:
            with pytest.raises(NotImplementedError):
                factory.create(input_type, chain_type)
            return

    result = factory.create(input_type, chain_type)
    assert result == "mocked_refine_documents_chain"
    mock_prompt_template.assert_called()
    mock_llm_chain.assert_called()
    mock_refine_documents_chain.assert_called()

    if input_type == SummaryInputType.SUMM:
        assert "internal_notes_summary" in factory.extra_input_variables

    assert factory.prompt_template is not None
    assert factory.refine_template is not None
