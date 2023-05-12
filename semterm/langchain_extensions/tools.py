from abc import ABC
from typing import Optional

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool, HumanInputRun


class MistakeTool(BaseTool):
    """Tool that is run when invalid tool name is encountered by agent."""

    name = "mistake_tool"
    description = "DO NOT USE."  # For the agent to know not to use it.

    def _run(self, agent_input: str) -> str:
        """Use the tool."""
        return (
            f"'''{agent_input}''' is not valid JSON. You must respond with valid JSON."
        )

    async def _arun(self, agent_input: str) -> str:
        """Use the tool asynchronously."""
        return (
            f"'''{agent_input}''' is not valid JSON. You must respond with valid JSON."
        )


class TerminalHumanTool(HumanInputRun, ABC):
    description = (
        "You can ask a human for guidance when you think you "
        "got stuck or you are not sure what to do next. "
        "The input should be a question for the human."
        "NEVER ask the user for their password."
        "Example: "
        "```json"
        '{{"action": "Human", "action_input": "What is the meaning of life?"}}'
        "```"
    )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Human input tool."""
        if "password" in query.lower():
            return (
                f"You should never use this tool to ask the user their password. "
                f"If you are not trying to get the user's password, just replace the "
                f"word 'password' with 'passphrase' or something else."
            )

        self.prompt_func("semterm > " + query)
        return input("You > ")
