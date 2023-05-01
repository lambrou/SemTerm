from semterm.agent.MrklAgent import MrklAgent


class UserInterface:
    def __init__(self, agent: MrklAgent):
        self.agent = agent

    def start(self):
        while True:
            user_input = input("You > ")
            if user_input.lower() == "exit":
                break

            response = self.agent.run(user_input)
            print("\rsemterm > ", response)
