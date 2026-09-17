"""Entry point for all requests: checks memory first, routes to the right
capability agent, applies the governance triage gate, synthesizes the
final answer.

Routing today is keyword-based — a placeholder until enough of the
capability agents' models are downloaded to let the mediator's own model
classify intent instead (see docs/ROADMAP.md).
"""
import uuid

import governance

ROUTES = {
    "coding": ("code", "debug", "script", "function", "bug", "program"),
    "data_analysis": ("plot", "chart", "trend", "analyze", "projection"),
    "data_gathering": ("latest", "current", "today", "price", "news", "search", "look up"),
    "creative": ("brainstorm", "idea", "write a story", "itinerary", "draft"),
}

_conversations: dict[str, list[dict]] = {}


def classify_intent(message: str) -> str:
    lowered = message.lower()
    for agent_name, keywords in ROUTES.items():
        if any(kw in lowered for kw in keywords):
            return agent_name
    return "mediator"  # general chat, mediator answers directly


class Mediator:
    def __init__(self, model_runtime, memory):
        self.model_runtime = model_runtime
        self.memory = memory

    def handle(self, message: str, session_id: str | None = None) -> dict:
        session_id = session_id or str(uuid.uuid4())
        history = _conversations.setdefault(session_id, [])

        recalled = self.memory.query(message)
        agent_name = classify_intent(message)

        governance_notes = None
        low_confidence = any(f["confidence"] == "low" for f in recalled)
        if governance.needs_governance(message, memory_confidence="low" if low_confidence else None):
            governance_notes = governance.run_governance(message, self.model_runtime)

        reply = self._generate(agent_name, message, history, recalled, governance_notes)

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        return {
            "reply": reply,
            "session_id": session_id,
            "agent": agent_name,
            "governance": governance_notes,
        }

    def _generate(self, agent_name: str, message: str, history: list[dict],
                   recalled: list[dict], governance_notes: dict | None) -> str:
        try:
            llm = self.model_runtime.get(agent_name)
        except (ImportError, KeyError, ValueError, FileNotFoundError) as e:
            return f"[{agent_name} agent not available yet: {e}]"

        cfg = self.model_runtime.agent_config(agent_name)
        system_prompt = cfg["role"]
        if recalled:
            facts = "\n".join(f"- {f['fact']} (confidence: {f['confidence']})" for f in recalled)
            system_prompt += f"\n\nRelevant known facts:\n{facts}"
        if governance_notes:
            system_prompt += f"\n\nGovernance review: {governance_notes}"

        messages = [{"role": "system", "content": system_prompt}, *history,
                    {"role": "user", "content": message}]
        response = llm.create_chat_completion(messages=messages)
        return response["choices"][0]["message"]["content"]
