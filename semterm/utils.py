from langchain.agents import load_tools, initialize_agent, AgentType, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationEntityMemory
from langchain.utilities.bash import BashProcess

from TerminalAgent import TerminalAgent


def get_tools():
    return [
        "terminal",
        "human",
    ]


def get_bash_mrkl():
    llm = ChatOpenAI(temperature=0)
    tools = load_tools(tool_names=get_tools(), llm=llm)
    memory = ConversationEntityMemory(
        llm=llm, return_messages=True, chat_history_key="chat_history"
    )
    TerminalAgent.update_forward_refs()
    terminal_agent = TerminalAgent.from_llm_and_tools(
        llm, tools, memory=memory, verbose=True
    )
    terminal_agent_executor = AgentExecutor.from_agent_and_tools(
        terminal_agent,
        tools,
        memory=memory,
        verbose=True,
    )
    return terminal_agent_executor
