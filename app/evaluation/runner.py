from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.agents.base import AgentResult
from app.agents.v001_minimal import AgentV001
from app.agents.v002_research import AgentV002
from app.agents.v003_rag import AgentV003
from app.agents.v004_deep_planner import AgentV004

logger = logging.getLogger(__name__)


AGENT_BY_VERSION = {
    "v001": AgentV001,
    "v002": AgentV002,
    "v003": AgentV003,
    "v004": AgentV004,
}


@dataclass
class EvalItem:
    item_id: str
    company: str
    question: str
    expected_answer: str


_TRAILING_COMMA_BEFORE_BRACE = re.compile(r",\s*}\s*$")


def _read_json_objects(path: Path) -> Iterable[dict[str, Any]]:
    """Read a file containing one JSON object after another, possibly with trailing commas.

    This is tolerant of the provided dataset format, which is not strict JSONL.
    """
    buf: list[str] = []
    depth = 0

    def _maybe_emit(buffer: list[str]) -> dict[str, Any] | None:
        if not buffer:
            return None
        raw = "\n".join(buffer)
        # Remove trailing commas before closing braces which are invalid in JSON
        cleaned_lines = []
        for ln in raw.splitlines():
            cleaned_lines.append(_TRAILING_COMMA_BEFORE_BRACE.sub("}", ln))
        cleaned = "\n".join(cleaned_lines)
        # Also handle the case where the trailing comma is on the previous line
        cleaned = re.sub(r",\s*\n(\s*})", r"\n\1", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            return None

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            buf.append(line.rstrip("\n"))
            depth += line.count("{") - line.count("}")
            if depth == 0:
                obj = _maybe_emit(buf)
                if obj is not None:
                    yield obj
                buf = []

        # Flush remainder
        if buf:
            obj = _maybe_emit(buf)
            if obj is not None:
                yield obj


"""LLM evaluation metrics are computed via MLflow GenAI in run_evaluation."""


def _get_agent_prompt(version: str) -> str:
    """Get the agent prompt for the given version."""
    prompt_path = Path(f"app/prompts/agent/{version}.txt")
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return f"Prompt for {version} not found"


def _eval_one(item: EvalItem, agent: Any) -> dict[str, Any]:
    """Evaluate a single item with the given agent."""
    try:
        agent_result: AgentResult = agent.run(
            company=item.company, question=item.question
        )
        return {
            "id": item.item_id,
            "company": item.company,
            "question": item.question,
            "expected_answer": item.expected_answer,
            "answer": agent_result.answer,
            "num_citations": len(agent_result.citations or []),
            "status": "success",
        }
    except Exception as e:
        return {
            "id": item.item_id,
            "company": item.company,
            "question": item.question,
            "expected_answer": item.expected_answer,
            "answer": f"ERROR: {str(e)}",
            "num_citations": 0,
            "status": "error",
        }


def run_evaluation(
    dataset_path: str, version: str, config: dict[str, Any], run_name: str | None = None
) -> None:
    dataset = Path(dataset_path)
    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset}")

    agent_cls = AGENT_BY_VERSION.get(version)
    if not agent_cls:
        raise ValueError(f"Unsupported version: {version}")

    # Resolve MLflow configuration
    mlcfg = dict(config.get("mlflow", {}))
    ml_enabled: bool = bool(mlcfg.get("enabled", True))
    tracking_uri: str = str(mlcfg.get("tracking_uri", ""))
    experiment_name: str = str(mlcfg.get("experiment", "adk_tutorial"))
    effective_run_name: str = (
        str(run_name) if run_name else str(mlcfg.get("run_name", f"eval-{version}"))
    )

    # Lazy import so we don't require mlflow unless enabled
    mlflow = None
    if ml_enabled:
        try:
            import mlflow as _mlflow  # type: ignore
            import pandas as pd  # type: ignore

            mlflow = _mlflow
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            if experiment_name:
                mlflow.set_experiment(experiment_name)
        except Exception as exc:  # pragma: no cover - optional integration
            logger.warning(f"MLflow disabled due to import/config error: {exc}")
            mlflow = None

    agent = agent_cls(config)

    items: list[EvalItem] = []
    for raw in _read_json_objects(dataset):
        items.append(
            EvalItem(
                item_id=str(raw.get("id", "")),
                company=str(raw.get("company", "")),
                question=str(raw.get("question", "")),
                expected_answer=str(raw.get("expected_answer", "")),
            )
        )

    logger.info(f"Processing {len(items)} items with {version} agent...")

    # Parallel processing with ThreadPoolExecutor
    max_workers = min(8, len(items))  # Cap at 8 workers to avoid overwhelming the API
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {
            executor.submit(_eval_one, item, agent): item for item in items
        }

        # Collect results as they complete
        for future in as_completed(future_to_item):
            try:
                result = future.result()
                results.append(result)
                if len(results) % 10 == 0:  # Progress indicator
                    logger.info(f"Completed {len(results)}/{len(items)} items...")
            except Exception as e:
                item = future_to_item[future]
                logger.error(f"Failed to evaluate item {item.item_id}: {e}")
                # Add error result
                results.append(
                    {
                        "id": item.item_id,
                        "company": item.company,
                        "question": item.question,
                        "expected_answer": item.expected_answer,
                        "answer": f"ERROR: {str(e)}",
                        "match_ratio": 0.0,
                        "num_citations": 0,
                        "status": "error",
                    }
                )

    # Calculate basic metric
    successful_results = [r for r in results if r["status"] == "success"]
    success_rate = len(successful_results) / len(results) if results else 0.0

    # Log to MLflow
    if mlflow is not None:
        with mlflow.start_run(run_name=effective_run_name):  # type: ignore[attr-defined]
            # Log parameters
            mlflow.log_params(  # type: ignore[attr-defined]
                {
                    "version": version,
                    "dataset": str(dataset),
                    "model": str(config.get("model", "")),
                    "steps": int(config.get("steps", 0)),
                    "max_workers": max_workers,
                }
            )

            # Log metrics
            mlflow.log_metric("success_rate", success_rate)  # type: ignore[attr-defined]
            mlflow.log_metric("total_items", len(results))  # type: ignore[attr-defined]
            mlflow.log_metric("successful_items", len(successful_results))  # type: ignore[attr-defined]

            # MLflow GenAI evaluation for LLM metrics (e.g., exact match, ROUGE-L)
            try:
                import pandas as pd  # type: ignore

                eval_df = pd.DataFrame(
                    {
                        "inputs": [
                            f"{r['company']} — {r['question']}" for r in results
                        ],
                        "predictions": [r["answer"] for r in results],
                        "ground_truth": [r["expected_answer"] for r in results],
                    }
                )

                eval_result = mlflow.evaluate(
                    data=eval_df,
                    predictions="predictions",
                    targets="ground_truth",
                    model_type="question-answering",
                    evaluators="default",
                    extra_metrics=[mlflow.metrics.genai.answer_similarity()],
                )

                # Log returned evaluator metrics
                for key, value in (getattr(eval_result, "metrics", {}) or {}).items():
                    try:
                        mlflow.log_metric(f"eval.{key}", float(value))
                    except Exception:
                        pass

                # Persist the evaluation table as an artifact
                genai_eval_path = (
                    Path("mlflow_eval_outputs") / f"genai_eval_{version}.csv"
                )
                genai_eval_path.parent.mkdir(parents=True, exist_ok=True)
                eval_df.to_csv(genai_eval_path, index=False)
                mlflow.log_artifact(str(genai_eval_path))  # type: ignore[attr-defined]
            except Exception as exc:
                logger.warning(f"GenAI evaluation skipped due to error: {exc}")

            # Log agent prompt as artifact
            prompt_content = _get_agent_prompt(version)
            prompt_path = Path("mlflow_eval_outputs") / f"prompt_{version}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt_content, encoding="utf-8")
            mlflow.log_artifact(str(prompt_path))  # type: ignore[attr-defined]

            # Log evaluation dataset as table artifact
            df = pd.DataFrame(results)  # type: ignore
            dataset_table_path = (
                Path("mlflow_eval_outputs") / f"evaluation_dataset_{version}.csv"
            )
            df.to_csv(dataset_table_path, index=False)
            mlflow.log_artifact(str(dataset_table_path))  # type: ignore[attr-defined]

            # Save detailed results as JSONL artifact
            results_path = (
                Path("mlflow_eval_outputs") / f"results_{version}_{dataset.stem}.jsonl"
            )
            with results_path.open("w", encoding="utf-8") as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            mlflow.log_artifact(str(results_path))  # type: ignore[attr-defined]

    # Console summary via logging
    logger.info(f"Completed {len(results)} examples")
    logger.info(f"Success rate: {success_rate:.1%}")
    if successful_results:
        logger.info(f"Successful evaluations: {len(successful_results)}")
    if len(results) - len(successful_results) > 0:
        logger.info(f"Failed evaluations: {len(results) - len(successful_results)}")
