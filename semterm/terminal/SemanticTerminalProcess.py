import re
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
        self.prompt = pid + " > "
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
    def _get_last_n_tokens(text: str, n: int = chunk_size, overlap: int = 200) -> str:
        """Return last n tokens from the output."""
        text_splitter = TokenTextSplitter(
            model_name=SemanticTerminalProcess.model_name,
            chunk_size=n,
            chunk_overlap=overlap,
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
        self.command = command
        self.prompt_prefix = ""
        if self.process is None:
            raise ValueError("Process not initialized")
        print("semterm > " + command)
        try:
            self.process.sendline(command)
            # self.process.expect(self.prompt)
            # self.process.sendline("")
            response = self._handle_terminal_response()

        except Exception as e:  # noqa - LLM is extremely error prone at the moment.
            prompt_prefix = (
                "The last command resulted in an error. Error: ",
                str(e),
            )
        output = self.process.before
        output = output.replace(command, "")
        if self.print_terminal_output:
            print(output)
        return SemanticTerminalProcess._get_last_n_tokens(str(prompt_prefix) + output)

    def _handle_terminal_response(self, command, timeout_count=0):
        password_regex = re.compile(
            r"(password for|Enter password|Password:|'s password:)", re.IGNORECASE
        )
        expect_dict = {
            "prompt": self.prompt,
            "password_request": password_regex,
            "EOF": pexpect.EOF,
            "TIMEOUT": pexpect.TIMEOUT,
        }
        list_index = self.process.expect(
            list(expect_dict.values()), timeout=self.timeout
        )
        response = expect_dict.keys()[list_index]
        if response == "password_request":
            self.process.sendline(
                input(
                    f"semterm is requesting your password to run the following command: {command}\n"
                    f"If you trust semterm, please enter your password below:\n"
                    f"Password: "
                )
            )
        elif response == "EOF":
            prompt_prefix = (
                "Process exited with error status: ",
                self.process.exitstatus,
            )
        elif response == "TIMEOUT":
            prompt_prefix = (
                "Process timed out. Timeout: ",
                self.timeout,
            )

    def get_most_recent_output(self):
        return self.process.buffer
