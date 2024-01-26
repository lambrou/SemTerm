from semterm.config.Config import Config
from semterm.agent.SemanticTerminalAgent import SemanticTerminalAgent
from semterm.UI.UserInterface import UserInterface


def main():
    config = Config()
    agent = SemanticTerminalAgent(config)
    UserInterface(agent).start()


if __name__ == "__main__":
    main()  # pragma: no cover
