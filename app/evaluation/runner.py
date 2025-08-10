from typing import Any, Dict


def run_evaluation(dataset_path: str, version: str, config: Dict[str, Any]) -> None:
    print(
        f"[EVAL] Running evaluation for {version} on {dataset_path} with config keys: {list(config.keys())}"
    )
