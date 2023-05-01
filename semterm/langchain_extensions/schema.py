from typing import NamedTuple


class AgentMistake(NamedTuple):
    """Class to use when an agent made a mistake and needs to be informed."""

    tool_input: str
    log: str
    tool: str = "mistake_tool"
