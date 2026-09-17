"""Governance layer: Ethics vs. Efficiency, arbitrated by Debate.

Only runs when the triage gate says a task warrants it — routine,
low-stakes actions skip governance entirely so every request doesn't
pay for a full Ethics -> Efficiency -> Debate pass.
"""
import re

IRREVERSIBLE_HINTS = re.compile(
    r"\b(delete|remove permanently|send|post|publish|buy|purchase|transfer|pay|cancel)\b",
    re.IGNORECASE,
)
OTHER_PERSON_HINTS = re.compile(
    r"\b(email|text|call|message|tell|notify)\s+\w+",
    re.IGNORECASE,
)


def needs_governance(message: str, memory_confidence: str | None = None, ambiguous: bool = False) -> bool:
    """Triage gate: irreversible, touches another person, low-confidence data, or ambiguous."""
    if IRREVERSIBLE_HINTS.search(message):
        return True
    if OTHER_PERSON_HINTS.search(message):
        return True
    if memory_confidence == "low":
        return True
    if ambiguous:
        return True
    return False


def run_governance(message: str, model_runtime) -> dict:
    """Run Ethics -> Efficiency -> Debate. Each agent needs its model downloaded
    and configured in agents/registry.yaml before this produces real output."""
    result = {"ethics": None, "efficiency": None, "debate": None}
    for role in ("ethics", "efficiency", "debate"):
        try:
            llm = model_runtime.get(role)
        except (ImportError, KeyError, ValueError, FileNotFoundError):
            result[role] = "(model not available yet)"
            continue
        cfg = model_runtime.agent_config(role)
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": cfg["role"]},
                {"role": "user", "content": message},
            ]
        )
        result[role] = response["choices"][0]["message"]["content"]
    return result
