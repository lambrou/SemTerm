from langchain.tools import BaseTool


class MistakeTool(BaseTool):
    """Tool that is run when invalid tool name is encountered by agent."""

    name = "mistake_tool"
    description = "DO NOT USE."  # For the agent to know not to use it.

    def _run(self, agent_input: str) -> str:
        """Use the tool."""
        return f"{agent_input} is not valid input, please correct your mistake and try again."

    async def _arun(self, agent_input: str) -> str:
        """Use the tool asynchronously."""
        return f"{agent_input} is not valid input, please correct your mistake and try again."
