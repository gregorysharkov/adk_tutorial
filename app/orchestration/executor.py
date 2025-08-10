from typing import Any


def execute_plan(plan: dict[str, Any]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = plan.get("plan", [])
    return {"status": "ok", "steps_executed": [s.get("id") for s in steps]}
