from unittest.mock import patch
from semterm.UI.UserInterface import UserInterface


class TestUserInterface:
    @patch("semterm.agent.MrklAgent.MrklAgent")
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["Hello", "exit"])
    def test_start(self, mock_input, mock_print, mock_mrkl_agent):
        mock_mrkl_agent.return_value.run.side_effect = lambda x: f"Mock response: {x}"

        user_interface = UserInterface(mock_mrkl_agent())
        user_interface.start()

        mock_input.assert_any_call("You > ")
        mock_print.assert_any_call("\rsemterm > ", "Mock response: Hello")
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1
