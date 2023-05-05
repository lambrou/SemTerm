from abc import ABC

import pytest
from unittest.mock import MagicMock, patch

from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
from pydantic import BaseModel

from semterm.agent.TerminalAgentExecutor import TerminalAgentExecutor
from semterm.langchain_extensions.schema import AgentMistake


class MockAgent(BaseModel):
    pass


class MockTool(BaseTool, ABC):
    name = "mock_tool"
    description = "Mock tool for testing purposes."

    def _run(self):
        pass

    def _arun(self):
        pass


class TestTerminalAgentExecutor:
    @pytest.fixture
    def executor(self):
        # Initialize an instance of TerminalAgentExecutor with mock parameters
        return TerminalAgentExecutor(
            max_iterations=10,
            verbose=True,
            memory={},
            callback_manager=None,
            agent=MockAgent(),
            tools={"tool1": MockTool()},
        )

    @patch.object(MockAgent, "plan", return_value=AgentFinish(return_values={}, log=""))
    def test_take_next_step_returns_finish(self, plan_mock, executor):
        # Test that _take_next_step returns AgentFinish when the output is an instance of AgentFinish
        output = AgentFinish(return_values={}, log="")
        result = executor._take_next_step({}, {}, {}, [output])
        assert result == output

    @patch.object(
        MockAgent,
        "plan",
        return_value=AgentAction(tool="tool1", tool_input="input1", log="input1"),
    )
    @patch.object(MockTool, "run", return_value="observation1")
    def test_take_next_step_returns_actions(self, run_mock, plan_mock, executor):
        # Test that _take_next_step returns a list of AgentAction and observation tuples
        name_to_tool_map = {"tool1": MockTool()}
        color_mapping = {"tool1": "red"}
        inputs = {"input1": "value1"}
        intermediate_steps = []
        result = executor._take_next_step(
            name_to_tool_map, color_mapping, inputs, intermediate_steps
        )
        assert len(result) == 1
        assert isinstance(result[0][0], AgentAction)
        assert result[0][0].tool == "tool1"
        assert result[0][0].tool_input == "input1"
        assert isinstance(result[0][1], str)
        assert result[0][1] == "observation1"

    @patch.object(
        MockAgent,
        "plan",
        return_value=AgentMistake(
            log="Invalid input", tool_input="input1", tool="tool1"
        ),
    )
    def test_take_next_step_returns_mistakes(self, plan_mock, executor):
        # Test that _take_next_step returns a list of AgentMistake and observation tuples
        name_to_tool_map = {}
        color_mapping = {}
        inputs = {}
        intermediate_steps = []
        result = executor._take_next_step(
            name_to_tool_map, color_mapping, inputs, intermediate_steps
        )
        assert len(result) == 1
        assert isinstance(result[0][0], AgentMistake)
        assert result[0][0].log == "Invalid input"
        assert result[0][0].tool_input == "input1"
        assert result[0][0].tool == "tool1"
        assert isinstance(result[0][1], str)
        assert result[0][1] == ""
