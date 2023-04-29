import os
from abc import ABC
from typing import Sequence, Optional, List, Tuple, Any

from langchain import BasePromptTemplate
from langchain.agents import ConversationalChatAgent, Agent, AgentOutputParser
from langchain.callbacks import BaseCallbackManager
from langchain.tools import BaseTool

from TerminalAgentPrompt import (
    PREFIX,
    SUFFIX,
    TEMPLATE_TOOL_RESPONSE,
)
from langchain.schema import (
    AgentAction,
    BaseOutputParser,
    BaseMessage,
    AIMessage,
    HumanMessage,
    BaseLanguageModel,
)


class TerminalAgent(ConversationalChatAgent, ABC):

    @classmethod
    def create_prompt(
        cls,
        tools: Sequence[BaseTool],
        system_message: str = PREFIX.format(current_directory=os.getcwd()),
        human_message: str = SUFFIX,
        input_variables: Optional[List[str]] = None,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> BasePromptTemplate:
        return super().create_prompt(
            tools=tools,
            system_message=system_message,
            human_message=human_message,
            input_variables=input_variables,
            output_parser=output_parser,
        )

    def _construct_scratchpad(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> List[BaseMessage]:
        thoughts: List[BaseMessage] = []
        for action, observation in intermediate_steps:
            thoughts.append(AIMessage(content=action.log))
            human_message = HumanMessage(
                content=TEMPLATE_TOOL_RESPONSE.format(observation=observation)
            )
            thoughts.append(human_message)
        return thoughts

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        callback_manager: Optional[BaseCallbackManager] = None,
        output_parser: Optional[AgentOutputParser] = None,
        system_message: str = PREFIX.format(current_directory=os.getcwd()),
        human_message: str = SUFFIX,
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Agent:
        return super().from_llm_and_tools(
            llm=llm,
            tools=tools,
            callback_manager=callback_manager,
            output_parser=output_parser,
            system_message=system_message,
            human_message=human_message,
            input_variables=input_variables,
            **kwargs,
        )
