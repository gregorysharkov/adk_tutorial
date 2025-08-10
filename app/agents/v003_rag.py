from typing import Any, Dict, List

from app.agents.base import AgentResult


class AgentV003:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def run(self, company: str, question: str) -> AgentResult:
        # Placeholder: pretend we retrieved k passages
        retrieved: List[str] = [
            "doc://kb/acme/overview.md#chunk-1",
            "doc://kb/acme/financials.pdf#chunk-12",
        ]
        answer = f"[V003] RAG-grounded answer about {company}: {{retrieved context + synthesis}}"
        return AgentResult(answer=answer, citations=retrieved)
