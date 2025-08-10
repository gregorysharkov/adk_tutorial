from typing import Any, TypedDict


class PlanStep(TypedDict):
    id: str
    type: str  # retrieve_rag | search_web | ask_user | read | synthesize
    inputs: dict[str, Any] | None
    when: str | None


def make_plan(
    question: str, *, max_steps: int = 20, max_questions: int = 3
) -> dict[str, Any]:
    return {
        "plan": [
            {
                "id": "step-1",
                "type": "retrieve_rag",
                "inputs": {"query": question},
                "when": None,
            },
            {
                "id": "step-2",
                "type": "search_web",
                "inputs": {"query": question},
                "when": "if recall low",
            },
            {
                "id": "step-3",
                "type": "ask_user",
                "inputs": None,
                "when": "if ambiguity blocks synthesis",
            },
            {"id": "step-4", "type": "synthesize", "inputs": None, "when": None},
        ],
        "budgets": {"max_steps": max_steps, "max_questions": max_questions},
    }
