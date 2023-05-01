from typing import Dict, Any, Union, Tuple, Sequence
from uuid import uuid4
from langchain.tools import BaseTool
from langchain.tools.base import get_filtered_args
from pydantic import validate_arguments

from semterm.terminal.SemanticTerminalManager import SemanticTerminalManager


class TerminalTool(BaseTool):
    name: str = "Terminal"
    description: str = (
        "Executes commands in a terminal. Input should be valid commands, and the output will be any "
        "output from running that command. If you are asked to do perform a task, it is likely the setup for the task "
        "has not been done yet. "
        "If you are unsure, use the Human tool to verify with the human that they want you to run all setup commands "
        "as well. "
    )
    manager: SemanticTerminalManager = SemanticTerminalManager()

    @property
    def func(self):
        return self.manager.create_process().run

    @property
    def args(self) -> dict:
        if self.args_schema is not None:
            return self.args_schema.schema()["properties"]
        else:
            inferred_model = validate_arguments(self.func).model
            return get_filtered_args(inferred_model, self.func)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """Use the tool."""
        return self.func(*args, **kwargs)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Use the tool asynchronously."""
        if self.coroutine:
            return await self.coroutine(*args, **kwargs)
        raise NotImplementedError("Tool does not support async")

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = self._to_args_and_kwargs_b_compat(tool_input)
        # For backwards compatibility. The tool must be run with a single input
        all_args = list(args) + list(kwargs.values())
        if len(all_args) != 1:
            raise ValueError(
                f"Too many arguments to single-input tool {self.name}."
                f" Args: {all_args}"
            )
        return tuple(all_args), {}

    @staticmethod
    def _to_args_and_kwargs_b_compat(
        run_input: Union[str, Dict]
    ) -> Tuple[Sequence, dict]:
        # For backwards compatability, if run_input is a string,
        # pass as a positional argument.
        if isinstance(run_input, str):
            return (run_input,), {}
        if isinstance(run_input, list):
            return [], {"command": ";".join(run_input)}
        else:
            return [], run_input
