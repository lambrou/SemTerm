from contextlib import contextmanager

import pytest
from unittest.mock import MagicMock, patch, Mock, create_autospec

from pydantic.decorator import validate_arguments

from semterm.terminal import TerminalTool, SemanticTerminalManager


class MockSemanticTerminalManager(SemanticTerminalManager.SemanticTerminalManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_process_mock = Mock()
        self._create_process_mock.run = Mock(return_value="Mocked response")

    def create_process(self, *args, **kwargs):
        return self._create_process_mock


class TestTerminalTool:
    @pytest.fixture(autouse=True)
    def setup_terminal_tool(self):
        self.terminal_tool = TerminalTool.TerminalTool(
            manager=MockSemanticTerminalManager()
        )

    def test_func(self):
        func = self.terminal_tool.func
        assert func() == "Mocked response"

    def test_run(self):
        result = self.terminal_tool._run("example_command")
        assert result == "Mocked response"

    def test_to_args_and_kwargs(self):
        args, kwargs = self.terminal_tool._to_args_and_kwargs("example_command")
        assert args == ("example_command",)
        assert kwargs == {}

        args, kwargs = self.terminal_tool._to_args_and_kwargs({"key": "value"})
        assert args == ("value",)
        assert kwargs == {}

        args, kwargs = self.terminal_tool._to_args_and_kwargs(["command1", "command2"])
        assert args == ("command1;command2",)
        assert kwargs == {}

    def test_to_args_and_kwargs_b_compat(self):
        args, kwargs = TerminalTool.TerminalTool._to_args_and_kwargs_b_compat(
            "example_command"
        )
        assert args == ("example_command",)
        assert kwargs == {}

        args, kwargs = TerminalTool.TerminalTool._to_args_and_kwargs_b_compat(
            {"key": "value"}
        )
        assert args == []
        assert kwargs == {"key": "value"}

        args, kwargs = TerminalTool.TerminalTool._to_args_and_kwargs_b_compat(
            ["command1", "command2"]
        )
        assert args == []
        assert kwargs == {"command": "command1;command2"}
