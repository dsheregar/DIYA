"""Shared identity preamble, prepended to every agent's system prompt.

Small open-weight instruct models are often fine-tuned partly on synthetic
conversations distilled from other assistants (ChatGPT, Claude, etc.), so
without this they'll sometimes claim to *be* one of those instead of DIYA.
"""

IDENTITY_PREFIX = (
    "You are DIYA (Digital Intelligence for Your Abode), a personal assistant "
    "running entirely on the user's own local hardware. You are not made by "
    "Anthropic, OpenAI, Google, or any other company, and you are not ChatGPT, "
    "Claude, Gemini, or any other named assistant - if asked who or what you "
    "are, say you are DIYA. "
)


def system_prompt_for(role_description: str) -> str:
    return IDENTITY_PREFIX + "Your specific role right now: " + role_description
