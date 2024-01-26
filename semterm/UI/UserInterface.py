from semterm.agent.SemanticTerminalAgent import SemanticTerminalAgent


class UserInterface:
    def __init__(self, agent: SemanticTerminalAgent):
        self.agent = agent

    def start(self):
        while True:
            user_input = input("You > ")
            if user_input.lower() == "exit":
                break

            response = self.agent.invoke(user_input)
            print("\rsemterm > ", response)
