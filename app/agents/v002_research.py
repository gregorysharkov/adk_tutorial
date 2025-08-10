from typing import Any, Dict

from app.agents.base import AgentResult


class AgentV002:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def run(self, company: str, question: str) -> AgentResult:
        answer = (
            f"[V002] Deep research answer about {company}: {{search + synthesis here}}"
        )
        citations = ["https://example.com/source1", "https://example.com/source2"]
        return AgentResult(answer=answer, citations=citations)
