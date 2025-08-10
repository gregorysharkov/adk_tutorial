from typing import Any, Dict

from app.agents.base import AgentResult, IAgent


class AgentV001:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def run(self, company: str, question: str) -> AgentResult:
        # Placeholder implementation
        answer = f"[V001] Answer about {company}: {{model output here}}"
        return AgentResult(answer=answer)
