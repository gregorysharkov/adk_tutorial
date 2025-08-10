from typing import Any

from app.agents.base import AgentResult


class AgentV004:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def run(self, company: str, question: str) -> AgentResult:
        answer = (
            f"[V004] Planned answer about {company}: {{execution trace + synthesis}}"
        )
        assumptions = ["Assumed fiscal year = calendar year"]
        return AgentResult(
            answer=answer, citations=[], assumptions=assumptions, trace_id="trace-0001"
        )
