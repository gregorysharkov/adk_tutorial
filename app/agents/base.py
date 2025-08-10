from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class AgentResult:
    answer: str
    citations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    trace_id: str | None = None


class IAgent(Protocol):
    config: dict[str, Any]

    def run(
        self, company: str, question: str
    ) -> AgentResult:  # pragma: no cover - interface
        ...
