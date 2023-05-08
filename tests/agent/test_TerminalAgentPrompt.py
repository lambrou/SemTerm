import semterm.agent.TerminalAgentPrompt as TerminalAgentPrompt


def test_terminal_agent_prompt_constants():
    assert hasattr(
        TerminalAgentPrompt, "TEMPLATE_TOOL_RESPONSE"
    ), "TEMPLATE_TOOL_RESPONSE constant not found."
    assert hasattr(TerminalAgentPrompt, "SUFFIX"), "SUFFIX constant not found."
    assert hasattr(
        TerminalAgentPrompt, "FORMAT_INSTRUCTIONS"
    ), "FORMAT_INSTRUCTIONS constant not found."
    assert hasattr(TerminalAgentPrompt, "PREFIX"), "PREFIX constant not found."
