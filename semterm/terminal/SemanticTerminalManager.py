import string
import random
from typing import Dict
from uuid import uuid4

from semterm.terminal.SemanticTerminalProcess import SemanticTerminalProcess


class SemanticTerminalManager:
    def __init__(self):
        self.processes: Dict[str, SemanticTerminalProcess] = {}

    def create_process(self, print_terminal_output=True, timeout=20):
        pid = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        process = SemanticTerminalProcess(pid, print_terminal_output, timeout)
        self.processes[process.pid] = process
        return process

    def get_process(self, pid):
        return self.processes.get(pid)

    def get_all_processes(self):
        if len(self.processes) == 0:
            return None
        return self.processes

    def kill_process(self, pid):
        if pid == "all":
            self.kill_all_processes()
            return True
        process = self.get_process(pid)
        if process is not None:
            try:
                process.kill()
                return True
            except Exception as e:
                return False
        return True

    def kill_all_processes(self):
        for pid in self.processes:
            self.kill_process(pid)

    def get_process_status(self, pid):
        process = self.get_process(pid)
        if process is not None:
            return process.get_process_status()
        return False

    def get_most_recent_output(self, pid):
        process = self.get_process(pid)
        if process is not None:
            return process.get_most_recent_output()
