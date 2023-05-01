from uuid import uuid4

from semterm.terminal.SemanticTerminalProcess import SemanticTerminalProcess


class SemanticTerminalManager:
    def __init__(self):
        self.processes = {}

    def create_process(self, print_terminal_output=True, timeout=20):
        process = SemanticTerminalProcess(str(uuid4()), print_terminal_output, timeout)
        self.processes[process.pid] = process
        return process

    def get_process(self, pid):
        return self.processes.get(pid)

    def get_most_recent_output(self, pid):
        process = self.get_process(pid)
        if process is not None:
            return process.get_most_recent_output()
