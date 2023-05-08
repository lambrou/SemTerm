import types

import pexpect
import pytest
import tiktoken
from unittest.mock import MagicMock, patch, call

from semterm.terminal.SemanticTerminalProcess import (
    SemanticTerminalProcess,
    TokenTextSplitter,
)


class TestSemanticTerminalProcess:
    @pytest.fixture
    def semantic_terminal_process(self, monkeypatch):
        original_method = SemanticTerminalProcess._initialize_persistent_process
        monkeypatch.setattr(
            SemanticTerminalProcess,
            "_initialize_persistent_process",
            MagicMock(return_value=MagicMock()),
        )
        instance = SemanticTerminalProcess(pid="test_pid")
        instance.original_initialize_persistent_process = types.MethodType(
            original_method, instance
        )
        return instance

    def test_initialize_persistent_process(
        self, semantic_terminal_process, monkeypatch
    ):
        semantic_terminal_process._initialize_persistent_process = (
            semantic_terminal_process.original_initialize_persistent_process
        )
        spawn_mock = MagicMock()
        monkeypatch.setattr(pexpect, "spawn", spawn_mock)

        semantic_terminal_process._initialize_persistent_process()

        spawn_mock.assert_called_with("bash", encoding="utf-8")
        spawn_mock.return_value.expect.assert_called_with(r"\$")
        spawn_mock.return_value.sendline.assert_called_with(
            "PS1=" + semantic_terminal_process.prompt
        )
        spawn_mock.return_value.expect_exact.assert_called_with(
            semantic_terminal_process.prompt, timeout=10
        )

    def test_tiktoken_encoder(self, semantic_terminal_process):
        with patch("tiktoken.Encoding.encode") as encode_mock:
            encode_mock.return_value = "test_encoded_value" * 10
            result = SemanticTerminalProcess._tiktoken_encoder("test_text")

            assert result == 10 * len("test_encoded_value")

    def test_get_last_n_tokens(self, semantic_terminal_process, monkeypatch):
        text_splitter_mock = MagicMock()
        monkeypatch.setattr(TokenTextSplitter, "split_text", text_splitter_mock)
        text_splitter_mock.return_value = ["sample1", "sample2", "sample3"]

        encoding_mock = MagicMock()
        monkeypatch.setattr(SemanticTerminalProcess, "_tiktoken_encoder", encoding_mock)
        encoding_mock.return_value = 100

        result = SemanticTerminalProcess._get_last_n_tokens("some_text", 250)

        assert result == "sample3"

    def test_get_last_n_tokens_last_two(self, semantic_terminal_process, monkeypatch):
        text_splitter_mock = MagicMock()
        monkeypatch.setattr(TokenTextSplitter, "split_text", text_splitter_mock)
        text_splitter_mock.return_value = ["sample1", "sample2", "sample3"]

        encoding_mock = MagicMock()
        monkeypatch.setattr(SemanticTerminalProcess, "_tiktoken_encoder", encoding_mock)
        encoding_mock.return_value = 100

        result = SemanticTerminalProcess._get_last_n_tokens("some_text", 2, 1)

        assert result == "Truncated Output: ...sample2sample3"

    def test_process_output(self, semantic_terminal_process):
        output = "output"
        command = "command"

        result = semantic_terminal_process.process_output(output, command)

        assert result == output

    def test_run_persistent(self, semantic_terminal_process, monkeypatch):
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.after = "test_prompt"

        monkeypatch.setattr(SemanticTerminalProcess, "_get_last_n_tokens", MagicMock())

        semantic_terminal_process._run_persistent("test_command")

        semantic_terminal_process.process.sendline.assert_has_calls(
            [call("test_command"), call("")], any_order=False
        )
        semantic_terminal_process.process.expect.assert_called_with(
            [semantic_terminal_process.prompt, pexpect.EOF],
            timeout=semantic_terminal_process.timeout,
        )

    def test_run_persistent_not_init(self, semantic_terminal_process, monkeypatch):
        semantic_terminal_process.process = None
        with pytest.raises(ValueError, match=r"not initialized"):
            semantic_terminal_process._run_persistent("test_command")

    def test_run_persistent_exception(self, semantic_terminal_process, monkeypatch):
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.sendline = MagicMock()
        monkeypatch.setattr(SemanticTerminalProcess, "_get_last_n_tokens", MagicMock())
        semantic_terminal_process.process.expect.side_effect = Exception(
            "Test Exception"
        )

        result = semantic_terminal_process._run_persistent("test_command")

        assert result.startswith(
            "The last command resulted in an error. Error: Test Exception"
        )

    def test_run_persistent_pexpect_eof(self, semantic_terminal_process, monkeypatch):
        monkeypatch.setattr(SemanticTerminalProcess, "_get_last_n_tokens", MagicMock())
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.sendline = MagicMock()
        semantic_terminal_process.process.expect.return_value = None
        semantic_terminal_process.process.after = pexpect.EOF
        semantic_terminal_process.process.exitstatus = 1

        result = semantic_terminal_process._run_persistent("test_command")

        assert result.startswith("Process exited with error status: 1")

    def test_get_most_recent_output(self, semantic_terminal_process):
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.buffer = "test_output"

        result = semantic_terminal_process.get_most_recent_output()

        assert result == "test_output"
