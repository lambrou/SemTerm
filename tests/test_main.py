from unittest.mock import MagicMock, patch
import semterm.main as semterm_main

from semterm.UI.UserInterface import UserInterface
from semterm.agent.MrklAgent import MrklAgent
from semterm.config.Config import Config


def test_main():
    with patch("semterm.main.Config", MagicMock(spec=Config)) as config_mock, patch(
        "semterm.main.MrklAgent", MagicMock(spec=MrklAgent)
    ) as agent_mock, patch(
        "semterm.main.UserInterface", MagicMock(spec=UserInterface)
    ) as ui_mock:
        semterm_main.main()

    # Check that the classes are instantiated and the start method is called on the UserInterface instance
    config_mock.assert_called_once()
    agent_mock.assert_called_once_with(config=config_mock.return_value)
    ui_mock.assert_called_once_with(agent=agent_mock.return_value)
    ui_mock.return_value.start.assert_called_once()
