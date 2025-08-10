from typing import Any, Dict

from app.agents.base import AgentResult


class AgentV004:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def run(self, company: str, question: str) -> AgentResult:
        plan_summary = "plan: [retrieve RAG] -> [search web if needed] -> [ask user if ambiguity persists] -> [synthesize]"
        answer = (
            f"[V004] Planned answer about {company}: {{execution trace + synthesis}}"
        )
        assumptions = ["Assumed fiscal year = calendar year"]
        return AgentResult(
            answer=answer, citations=[], assumptions=assumptions, trace_id="trace-0001"
        )
