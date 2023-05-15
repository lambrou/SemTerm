from abc import ABC
from typing import Optional, Any, Union, List

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool

from semterm.terminal.SemanticTerminalManager import SemanticTerminalManager


class ProcessManagerTool(BaseTool, ABC):
    name = "ProcessManager"
    description = (
        "You can use this tool to list all processes you've spawned, get a process' "
        "details and most recent output, kill a process, or send a command to a running process.\n"
        "This is not the same as running a `ps aux` command. This is a list of processes you have spawned.\n"
        "The input should be a `get`, `list`, `send`, or `kill` command.\n"
        "get params: `pid` (required)\nlist params: none\nkill params: `pid` (required) or `all`\n"
        "send params: `pid` (required), `input` (must be a bash command) (required)\n"
        "You can send `ctrlc` to a process to send a keyboard interrupt.\n"
        "get returns: `pid`, `command`, `status`, `output` \n"
        "list returns: `pid`, `command`, `status`\n"
        "kill returns: `success` or `failure`\n"
        "send returns: The Terminal Output of the command you sent.\n"
        "Examples:\n"
        "```json\n"
        '{{"action": "ProcessManager", "action_input": "list"}}\n'
        "```\n"
        "Returns:\n"
        "```bash\n"
        "1234 - python3 server.py - running\n"
        "5678 - tail ps aux - running\n"
        "```\n"
        "```json\n"
        '{{"action": "ProcessManager", "action_input": "get 5678"}}\n'
        "```\n"
        "Returns:\n"
        "```bash\n"
        "5678 - tail ps aux - running - Output: root     24670  0.0  0.0   1848   468 S    May05   0:00 /init\n"
        "```\n"
        "```json\n"
        '{{"action": "ProcessManager", "action_input": "send 5678 ctrlc"}}\n'
        "```\n"
        "Returns:\n"
        "```bash\n"
        "root     24670  0.0  0.0   1848   468 S    May05   0:00 /init\n^C\n"
        "```\n"
        "```json\n"
        '{{"action": "ProcessManager", "action_input": ["kill 5678", "send 1234 ls"]}}\n'
        "```\n"
    )
    manager: SemanticTerminalManager = SemanticTerminalManager()

    def _run(
        self,
        action_input: Union[str, List[str]],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Process Manager tool."""
        if isinstance(action_input, str):
            action_input = [action_input]
        for action in action_input:
            commands = ["get", "list", "kill", "send"]
            action = action.split(" ")
            command = action[0]
            output = ""

            if command == "get":
                output += f"Command: {action} Output:\n{self.get_process(action[1])}\n"
            elif command == "list":
                output += f"Command: {action} Output:\n{self.list_processes()}\n"
            elif command == "kill":
                output += f"Command: {action} Output:\n{self.kill_process(action[1])}\n"
            elif command == "send":
                output += f"Command: {action} Output:\n{self.send_command(action[1], ' '.join(action[2:]))}\n"
            else:
                output += f"Command: {action} Output:\nInvalid command.\nValid commands are: {', '.join(commands)}.\n"
        return output

    async def _arun(self, *args: Any, **kwargs: Any) -> str:  # pragma: no cover
        """Use the tool asynchronously."""
        if self.coroutine:
            return await self.coroutine(*args, **kwargs)
        raise NotImplementedError("Tool does not support async")

    def get_process(self, pid: str) -> str:
        process = self.manager.get_process(pid)
        if process:
            status = self.manager.get_process_status(pid)
            output = self.manager.get_most_recent_output(pid)
            truncated_output = process.get_last_n_tokens(output)
            return f"PID: {pid}\nCommand: {process.get_most_recent_command() if process.get_most_recent_command() else 'bash'}\nStatus: {status}\nOutput:\n{truncated_output}"
        else:
            return f"Process {pid} not found."

    def list_processes(self) -> str:
        processes = self.manager.get_all_processes()
        if processes:
            return "\n".join(
                [
                    f"PID: {pid}\nCommand: {p.get_most_recent_command() if p.get_most_recent_command() else 'bash'} Status: {p.get_process_status()}\n"
                    for pid, p in processes.items()
                ]
            )
        else:
            return "No running processes."

    def kill_process(self, pid: str) -> str:
        success = self.manager.kill_process(pid)
        if success:
            return f"Process terminated successfully."
        else:
            return f"Failed to terminate process {pid}."

    def send_command(self, pid: str, command: str) -> str:
        process = self.manager.get_process(pid)
        if process:
            if command == "ctrlc":
                return process.send_keyboard_interrupt()
            return process.run(command)
        else:
            return f"Process {pid} not found."
