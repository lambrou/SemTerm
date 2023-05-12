from contextlib import contextmanager

import pytest
from unittest.mock import MagicMock, patch, Mock, create_autospec

from pydantic import BaseModel
from pydantic.decorator import validate_arguments

from semterm.terminal import TerminalTool, SemanticTerminalManager
from semterm.terminal.SemanticTerminalProcess import SemanticTerminalProcess


class MockSemanticTerminalManager(SemanticTerminalManager.SemanticTerminalManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_process(self, *args, **kwargs):
        return MockSemanticTerminalProcess()


class MockSemanticTerminalProcess(SemanticTerminalProcess):
    def __init__(self, *args, **kwargs):
        pass

    def _initialize_persistent_process(self):
        return None

    def run(self, *args, **kwargs):
        return "Mocked response"

    def _run(self, *args, **kwargs):
        return "Mocked response"


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

    def test_args_with_args_schema(self):
        class ArgsSchema(BaseModel):
            arg1: int
            arg2: str

        self.terminal_tool.args_schema = ArgsSchema

        expected_args = {
            "arg1": {"title": "Arg1", "type": "integer"},
            "arg2": {"title": "Arg2", "type": "string"},
        }

        assert self.terminal_tool.args == expected_args

    def test_args_without_args_schema(self):
        def dummy_function(arg1: int, arg2: str):
            return "Dummy response"

        type(self.terminal_tool).func = property(lambda _: dummy_function)

        expected_args = {
            "arg1": {"title": "Arg1", "type": "integer"},
            "arg2": {"title": "Arg2", "type": "string"},
        }

        assert self.terminal_tool.args == expected_args

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

        with pytest.raises(ValueError, match=r"Too many arguments"):
            self.terminal_tool._to_args_and_kwargs(
                {"command1": "value", "command2": "value"}
            )

    def test_to_args_and_kwargs_b_compat(self):
        args, kwargs = self.terminal_tool._to_args_and_kwargs_b_compat(
            "example_command"
        )
        assert args == ("example_command",)
        assert kwargs == {}

        args, kwargs = self.terminal_tool._to_args_and_kwargs_b_compat({"key": "value"})
        assert args == []
        assert kwargs == {"key": "value"}

        args, kwargs = self.terminal_tool._to_args_and_kwargs_b_compat(
            ["command1", "command2"]
        )
        assert args == []
        assert kwargs == {"command": "command1;command2"}
