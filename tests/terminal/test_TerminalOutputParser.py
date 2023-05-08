import pytest
from typing import Union
from langchain.schema import AgentAction, AgentFinish
from semterm.agent.TerminalAgentPrompt import FORMAT_INSTRUCTIONS
from semterm.langchain_extensions.schema import AgentMistake
from semterm.terminal.TerminalOutputParser import (
    TerminalOutputParser,
)


class TestTerminalOutputParser:
    @pytest.fixture
    def parser(self):
        return TerminalOutputParser()

    def test_get_format_instructions(self, parser):
        assert parser.get_format_instructions() == FORMAT_INSTRUCTIONS

    @pytest.mark.parametrize(
        "text, expected",
        [
            (
                '{"action": "Final Answer", "action_input": "42"}',
                AgentFinish(
                    {"output": "42"}, '{"action": "Final Answer", "action_input": "42"}'
                ),
            ),
            (
                'Something before {"action": "Test Action", "action_input": "test input"} and after',
                AgentAction(
                    "Test Action",
                    "test input",
                    'Something before {"action": "Test Action", "action_input": "test input"} and after',
                ),
            ),
            (
                "This is a text without valid JSON",
                AgentMistake(
                    "This is a text without valid JSON",
                    "This is a text without valid JSON",
                ),
            ),
            (
                '{"action": "Incomplete JSON", "action_input":',
                AgentMistake(
                    '{"action": "Incomplete JSON", "action_input":',
                    '{"action": "Incomplete JSON", "action_input":',
                ),
            ),
            (
                "{'action': 'Invalid JSON', 'action_input': thisiswrong}",
                AgentMistake(
                    "{'action': 'Invalid JSON', 'action_input': thisiswrong}",
                    "{'action': 'Invalid JSON', 'action_input': thisiswrong}",
                ),
            ),
        ],
    )
    def test_parse(self, parser, text: str, expected: Union[AgentAction, AgentFinish]):
        result = parser.parse(text)
        assert result == expected
