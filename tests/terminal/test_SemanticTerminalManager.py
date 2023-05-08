import pytest
from unittest.mock import MagicMock
from semterm.terminal.SemanticTerminalManager import SemanticTerminalManager
from semterm.terminal.SemanticTerminalProcess import SemanticTerminalProcess


class TestSemanticTerminalManager:
    @pytest.fixture
    def semantic_terminal_manager(self):
        return SemanticTerminalManager()

    @pytest.fixture
    def mock_semantic_terminal_process(self, monkeypatch):
        mock_instance = MagicMock()
        mock_instance.pid = "mock_pid"

        monkeypatch.setattr(
            SemanticTerminalProcess, "__new__", MagicMock(return_value=mock_instance)
        )
        return mock_instance

    def test_create_process(self, semantic_terminal_manager):
        process = semantic_terminal_manager.create_process()
        assert process.pid in semantic_terminal_manager.processes

    def test_get_process(self, semantic_terminal_manager):
        process = semantic_terminal_manager.create_process()
        fetched_process = semantic_terminal_manager.get_process(process.pid)

        assert process == fetched_process

    def test_get_most_recent_output(self, semantic_terminal_manager, monkeypatch):
        monkeypatch.setattr(
            SemanticTerminalProcess,
            "get_most_recent_output",
            MagicMock(return_value="test_output"),
        )
        process = semantic_terminal_manager.create_process()
        output = semantic_terminal_manager.get_most_recent_output(process.pid)

        assert output == "test_output"

    def test_get_most_recent_output_invalid_pid(self, semantic_terminal_manager):
        output = semantic_terminal_manager.get_most_recent_output("invalid_pid")

        assert output is None
