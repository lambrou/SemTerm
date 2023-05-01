import subprocess
from typing import Any

import pexpect as pexpect
import tiktoken
from langchain.utilities import BashProcess
from langchain.text_splitter import TokenTextSplitter


class SemanticTerminalProcess(BashProcess):
    model_name: str = "gpt-3.5-turbo"
    chunk_size: int = 500

    def __init__(self, pid, print_terminal_output=True, timeout=20):
        self.print_terminal_output = print_terminal_output
        self.timeout = timeout
        self.pid = pid
        self.prompt = pid
        self.process = self._initialize_persistent_process()

    def _initialize_persistent_process(self) -> pexpect.spawn:
        process = pexpect.spawn(
            "bash",
            encoding="utf-8",
        )
        process.expect(r"\$")
        process.sendline("PS1=" + self.prompt)
        process.expect_exact(self.prompt, timeout=10)
        return process

    @staticmethod
    def _tiktoken_encoder(text: str, **kwargs: Any) -> int:
        encoder = tiktoken.encoding_for_model(SemanticTerminalProcess.model_name)
        return len(encoder.encode(text, **kwargs))

    @staticmethod
    def _get_last_n_tokens(text: str, n: int = chunk_size) -> str:
        """Return last n tokens from the output."""
        text_splitter = TokenTextSplitter(
            model_name=SemanticTerminalProcess.model_name,
            chunk_size=n,
        )
        split_text = text_splitter.split_text(text)
        last = split_text[-1]
        if SemanticTerminalProcess._tiktoken_encoder(last) < n:
            return last
        else:
            return "Truncated Output: ..." + "".join(split_text[-2:])

    def process_output(self, output: str, command: str) -> str:
        """Process the output."""
        return output

    def _run_persistent(self, command: str) -> str:
        """Run commands and return final output."""
        prompt_prefix = ""
        if self.process is None:
            raise ValueError("Process not initialized")
        print("semterm > " + command)
        try:
            self.process.sendline(command)
            self.process.expect(self.prompt)
            self.process.sendline("")
            self.process.expect([self.prompt, pexpect.EOF], timeout=self.timeout)
        except Exception as e:  # noqa - LLM is extremely error prone at the moment.
            prompt_prefix = (
                "The last command resulted in an error. Error: ",
                str(e),
            )
        if self.process.after == pexpect.EOF:
            prompt_prefix = (
                "Process exited with error status: ",
                self.process.exitstatus,
            )
        output = self.process.before
        if self.print_terminal_output:
            print(output.replace(command, ""))
        return SemanticTerminalProcess._get_last_n_tokens(str(prompt_prefix) + output)

    def get_most_recent_output(self):
        return self.process.buffer
