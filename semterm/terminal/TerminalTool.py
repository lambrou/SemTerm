from typing import Dict, Any, Union, Tuple, Sequence, Literal, List
from uuid import uuid4
from langchain.tools import BaseTool
from langchain.tools.base import get_filtered_args, StructuredTool
from pydantic import BaseModel, Field
from pydantic.decorator import validate_arguments

from semterm.terminal.SemanticTerminalManager import SemanticTerminalManager


class TerminalToolSchema(BaseModel):
    """Schema for the TerminalTool."""

    action: Literal["list", "new", "get", "send", "kill"] = Field(
        "The action to take. Must be one of: list, new, get, send, kill."
    )
    pid: str = Field(
        'The PID of the process to perform the action on. Required for "get", "send", and "kill" actions.'
    )
    command: Union[str, List[str]] = Field(
        "The command or commands to run. If multiple commands, send a list of strings."
    )


class TerminalTool(StructuredTool):
    name: str = "Terminal"
    description: str = (
        "This tool is used to spawn bash processes and run commands on those processes. "
        "If you are asked to perform a task, it is likely the setup for the task "
        "has not been done yet.\n"
        "Examples:\n"
        "```json\n"
        '{{"action": "Terminal", "action_input": {{"action": "new", "command": "ls"}}}}\n'
        "```\n"
        "```json\n"
        '{{"action": "Terminal", "action_input": {{"action": "get", "pid": "1234"}}}}\n'
        "```\n"
        "```json\n"
        '{{"action": "Terminal", "action_input": {{"action": "send", "pid": "1234", "command": "ls"}}}}\n'
        "```\n"
        "```json\n"
        '{{"action": "Terminal", "action_input": {{"action": "kill", "pid": "1234"}}}}\n'
        "```\n"
        "```json\n"
        '{{"action": "Terminal", "action_input": {{"action": "list"}}}}\n'
        "```\n"
    )
    manager: SemanticTerminalManager = SemanticTerminalManager()
    args_schema = TerminalToolSchema()
    args = ["list", "new", "get", "send", "kill"]

    @property
    def func(self):
        return self.manager.create_process().run

    def _handle_llm_input(self, llm_input: Dict[str, Any]) -> Tuple:
        """Handle the input from the LLM."""
        action = llm_input["action_input"]["action"]
        pid = llm_input["action_input"].get("pid")
        command = llm_input["action_input"].get("command")
        return action, pid, command

    # @property
    # def args(self) -> dict:
    #     if self.args_schema is not None:
    #         return self.args_schema.schema()["properties"]
    #     else:
    #         inferred_model = validate_arguments(self.func).model
    #         return get_filtered_args(inferred_model, self.func)

    # def _run(self, *args: Any, **kwargs: Any) -> str:
    #     """Use the tool."""
    #     return self.func(*args, **kwargs)
    #
    # async def _arun(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
    #     """Use the tool asynchronously."""
    #     if self.coroutine:
    #         return await self.coroutine(*args, **kwargs)
    #     raise NotImplementedError("Tool does not support async")

    # def _to_args_and_kwargs(
    #     self, tool_input: Union[str, Dict, list[str]]
    # ) -> Tuple[Tuple, Dict]:
    #     """Convert tool input to pydantic model."""
    #     args, kwargs = self._to_args_and_kwargs_b_compat(tool_input)
    #     # For backwards compatibility. The tool must be run with a single input
    #     all_args = list(args) + list(kwargs.values())
    #     if len(all_args) != 1:
    #         raise ValueError(
    #             f"Too many arguments to single-input tool {self.name}."
    #             f" Args: {all_args}"
    #         )
    #     return tuple(all_args), {}
    #
    # @staticmethod
    # def _to_args_and_kwargs_b_compat(
    #     run_input: Union[str, Dict, list[str]]
    # ) -> Tuple[Sequence, dict]:
    #     # For backwards compatability, if run_input is a string,
    #     # pass as a positional argument.
    #     if isinstance(run_input, str):
    #         return (run_input,), {}
    #     if isinstance(run_input, list):
    #         return [], {"command": ";".join(run_input)}
    #     else:
    #         return [], run_input
