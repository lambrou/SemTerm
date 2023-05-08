from pytest import mark
import pytest
from semterm.langchain_extensions.tools import MistakeTool


class TestMistakeTool:
    @pytest.fixture
    def mistake_tool(self):
        return MistakeTool()

    def test_run(self, mistake_tool):
        agent_input = "invalid_input"
        expected_output = f"{agent_input} is not valid input, please correct your mistake and try again."
        output = mistake_tool.run(agent_input)
        assert output == expected_output

    @pytest.mark.asyncio
    async def test_arun(self, mistake_tool):
        agent_input = "invalid_input"
        expected_output = f"{agent_input} is not valid input, please correct your mistake and try again."
        output = await mistake_tool.arun(agent_input)
        assert output == expected_output
