from typing import Any, Dict, List


def execute_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = plan.get("plan", [])
    return {"status": "ok", "steps_executed": [s.get("id") for s in steps]}
