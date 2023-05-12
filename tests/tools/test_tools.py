from unittest.mock import patch
import pytest
from semterm.langchain_extensions.tools import MistakeTool, TerminalHumanTool


class TestMistakeTool:
    @pytest.fixture
    def mistake_tool(self):
        return MistakeTool()

    def test_run(self, mistake_tool):
        agent_input = "invalid_input"
        expected_output = (
            f"'''{agent_input}''' is not valid JSON. You must respond with valid JSON."
        )
        output = mistake_tool.run(agent_input)
        assert output == expected_output

    @pytest.mark.asyncio
    async def test_arun(self, mistake_tool):
        agent_input = "invalid_input"
        expected_output = (
            f"'''{agent_input}''' is not valid JSON. You must respond with valid JSON."
        )
        output = await mistake_tool.arun(agent_input)
        assert output == expected_output


class TestTerminalHumanTool:
    @pytest.fixture
    def human_tool(self):
        return TerminalHumanTool()

    def test_run(self, human_tool):
        agent_input = "What is the meaning of life?"
        expected_output = "You > "
        with patch("builtins.input", return_value=expected_output):
            output = human_tool.run(agent_input)
        assert output == expected_output

    def test_run_with_password_request(self, human_tool):
        agent_input = "What is your password?"
        expected_output = (
            f"You should never use this tool to ask the user their password. "
            f"If you are not trying to get the user's password, just replace the "
            f"word 'password' with 'passphrase' or something else."
        )
        output = human_tool.run(agent_input)
        assert output == expected_output
