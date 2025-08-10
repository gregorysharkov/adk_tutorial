from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol


@dataclass
class AgentResult:
    answer: str
    citations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    trace_id: str | None = None


class IAgent(Protocol):
    config: Dict[str, Any]

    def run(
        self, company: str, question: str
    ) -> AgentResult:  # pragma: no cover - interface
        ...
