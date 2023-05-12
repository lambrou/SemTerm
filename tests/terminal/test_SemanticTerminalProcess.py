import types
import pexpect
import pytest
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

    def test_run_persistent_basic_command(self, semantic_terminal_process, monkeypatch):
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.after = "test_prompt"
        semantic_terminal_process.process.expect.return_value = 0

        monkeypatch.setattr(SemanticTerminalProcess, "_get_last_n_tokens", MagicMock())

        semantic_terminal_process._run_persistent("ls")

        semantic_terminal_process.process.sendline.assert_has_calls(
            [call("ls")], any_order=False
        )
        assert semantic_terminal_process.prompt in semantic_terminal_process.process.expect.call_args[0][0]

    def test_run_persistent_elevated_command(self, semantic_terminal_process, monkeypatch):
        fake_password = "password123"
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.after = "test_prompt"
        semantic_terminal_process.process.expect.return_value = 1

        monkeypatch.setattr(SemanticTerminalProcess, "_get_last_n_tokens", MagicMock())
        monkeypatch.setattr("getpass.getpass", MagicMock(return_value=fake_password))

        semantic_terminal_process._run_persistent("sudo ls")
        semantic_terminal_process.process.sendline.assert_has_calls(
            [call("sudo ls"), call(fake_password)], any_order=False
        )
        assert semantic_terminal_process.prompt in semantic_terminal_process.process.expect.call_args[0][0]

    def test_run_persistent_not_init(self, semantic_terminal_process, monkeypatch):
        semantic_terminal_process.process = None
        with pytest.raises(ValueError, match=r"not initialized"):
            semantic_terminal_process._run_persistent("ls")

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

    def test_handle_terminal_response_EOF(self, semantic_terminal_process):
        command = "command"
        response = "EOF"
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.exitstatus = 1
        result = semantic_terminal_process._handle_terminal_response(command, response)
        assert result == "Process exited with error status: 1"

    def test_handle_terminal_response_TIMEOUT(self, semantic_terminal_process):
        command = "command"
        response = "TIMEOUT"
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.buffer = "test buffer"
        result = semantic_terminal_process._handle_terminal_response(command, response)
        assert result == "Timeout reached. Most recent output: test buffer"

    @patch.object(SemanticTerminalProcess, '_handle_stdout', return_value='test')
    @patch('getpass.getpass', return_value='password')
    def test_handle_password_request_keyboard_interrupt(self, mock_getpass, mock_handle_stdout, semantic_terminal_process):
        command = "command"
        semantic_terminal_process.process.sendline.side_effect = self.raise_keyboard_interrupt
        result = semantic_terminal_process._handle_password_request(command)
        semantic_terminal_process.process.sendintr.assert_called_once()
        assert result == "User aborted password request."

    def raise_keyboard_interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    def test_keyboard_interrupt_handler(self):
        with pytest.raises(KeyboardInterrupt):
            SemanticTerminalProcess.keyboard_interrupt_handler(1, 2)

    def test_handle_terminal_response_password_request(self, semantic_terminal_process):
        command = "command"
        response = "password_request"
        semantic_terminal_process._handle_password_request = MagicMock(return_value="test")
        result = semantic_terminal_process._handle_terminal_response(command, response)
        assert result == "test"

    def test_handle_terminal_response_incorrect_password_exceeded_attempts(self, semantic_terminal_process):
        command = "command"
        response = "incorrect_password"
        semantic_terminal_process.incorrect_password_attempts = 3
        result = semantic_terminal_process._handle_terminal_response(command, response)
        assert result == "Too many bad pass attempts."

    def test_handle_terminal_response_incorrect_password_within_attempts(self, semantic_terminal_process):
        command = "command"
        response = "incorrect_password"
        semantic_terminal_process.incorrect_password_attempts = 2
        semantic_terminal_process._handle_password_request = MagicMock(return_value="test")
        result = semantic_terminal_process._handle_terminal_response(command, response)
        assert result == "test"
        assert semantic_terminal_process.incorrect_password_attempts == 3

    def test_get_most_recent_output(self, semantic_terminal_process):
        semantic_terminal_process.process = MagicMock()
        semantic_terminal_process.process.buffer = "test_output"

        result = semantic_terminal_process.get_most_recent_output()

        assert result == "test_output"
