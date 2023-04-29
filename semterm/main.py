import sys
from utils import get_bash_mrkl
from dotenv import load_dotenv

load_dotenv()


def main():
    user_input = " ".join(sys.argv[1:])
    mrkl_agent = get_bash_mrkl()
    response = mrkl_agent.run(input=user_input)
    print(response)


if __name__ == "__main__":
    main()
