from __future__ import annotations

import json
import logging
import os
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

MLFLOW_OUTPUT_DIR = Path("mlflow_eval_outputs")

# Dataset paths - hardcoded constants (relative to project root)
ORIGINAL_DATASET_PATH = (
    Path(__file__).parent.parent.parent
    / "data"
    / "datasets"
    / "company_qa_eval_100.jsonl"
)
TRANSFORMED_DATASET_PATH = (
    Path(__file__).parent.parent.parent
    / "data"
    / "datasets"
    / "transformed_companies_qa.jsonl"
)


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

    Args:
        path: Path to the JSONL file to read.

    Yields:
        dict[str, Any]: Parsed JSON objects from the file.
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


def _load_eval_items(dataset: Path | None = None) -> list[EvalItem]:
    """Load evaluation items from both the original and transformed datasets.

    Args:
        dataset: Optional path to a specific dataset file. If None, loads from both
                hardcoded dataset paths.

    Returns:
        list[EvalItem]: List of evaluation items parsed from the dataset(s).
    """
    items: list[EvalItem] = []

    if dataset is not None:
        # Load from specific dataset if provided
        for raw in _read_json_objects(dataset):
            items.append(
                EvalItem(
                    item_id=str(raw.get("id", "")),
                    company=str(raw.get("company", "")),
                    question=str(raw.get("question", "")),
                    expected_answer=str(raw.get("expected_answer", "")),
                )
            )
    else:
        # Load from both hardcoded datasets
        datasets_to_load = [ORIGINAL_DATASET_PATH, TRANSFORMED_DATASET_PATH]

        for dataset_path in datasets_to_load:
            if dataset_path.exists():
                logger.info(f"Loading dataset: {dataset_path}")
                for raw in _read_json_objects(dataset_path):
                    items.append(
                        EvalItem(
                            item_id=str(raw.get("id", "")),
                            company=str(raw.get("company", "")),
                            question=str(raw.get("question", "")),
                            expected_answer=str(raw.get("expected_answer", "")),
                        )
                    )
                logger.info(
                    f"Loaded {len([i for i in items if i.company in str(dataset_path)])} items from {dataset_path.name}"
                )
            else:
                logger.warning(f"Dataset not found: {dataset_path}")

    logger.info(f"Total evaluation items loaded: {len(items)}")
    return items


def get_dataset_stats() -> dict[str, Any]:
    """Get statistics about the available datasets.

    Returns:
        dict[str, Any]: Dictionary containing dataset statistics.
    """
    stats = {}

    # Check original dataset
    if ORIGINAL_DATASET_PATH.exists():
        original_items = list(_read_json_objects(ORIGINAL_DATASET_PATH))
        stats["original_dataset"] = {
            "path": str(ORIGINAL_DATASET_PATH),
            "item_count": len(original_items),
            "companies": list(
                set(
                    item.get("company", "")
                    for item in original_items
                    if item.get("company")
                )
            ),
        }
    else:
        stats["original_dataset"] = {
            "path": str(ORIGINAL_DATASET_PATH),
            "status": "not_found",
        }

    # Check transformed dataset
    if TRANSFORMED_DATASET_PATH.exists():
        transformed_items = list(_read_json_objects(TRANSFORMED_DATASET_PATH))
        stats["transformed_dataset"] = {
            "path": str(TRANSFORMED_DATASET_PATH),
            "item_count": len(transformed_items),
            "companies": list(
                set(
                    item.get("company", "")
                    for item in transformed_items
                    if item.get("company")
                )
            ),
        }
    else:
        stats["transformed_dataset"] = {
            "path": str(TRANSFORMED_DATASET_PATH),
            "status": "not_found",
        }

    # Combined stats
    if ORIGINAL_DATASET_PATH.exists() and TRANSFORMED_DATASET_PATH.exists():
        combined_items = list(_read_json_objects(ORIGINAL_DATASET_PATH)) + list(
            _read_json_objects(TRANSFORMED_DATASET_PATH)
        )
        stats["combined"] = {
            "total_items": len(combined_items),
            "total_companies": len(
                set(
                    item.get("company", "")
                    for item in combined_items
                    if item.get("company")
                )
            ),
        }

    return stats


def run_evaluation_on_combined_datasets(
    version: str = "v001",
    config: dict[str, Any] | None = None,
    run_name: str | None = None,
) -> None:
    """Convenience function to run evaluation on both datasets combined.

    Args:
        version: Agent version to evaluate (e.g., 'v001', 'v002').
        config: Configuration dictionary containing agent and MLflow settings.
        run_name: Optional custom name for the MLflow run.
    """
    logger.info(
        "Running evaluation on combined datasets (original + transformed companies)"
    )
    run_evaluation(dataset_path=None, version=version, config=config, run_name=run_name)


def _get_agent_prompt(version: str) -> str:
    """Get the agent prompt for the given version.

    Args:
        version: Agent version string (e.g., 'v001', 'v002').

    Returns:
        str: The prompt content for the specified agent version.
    """
    prompt_path = Path(f"app/prompts/agent/{version}.txt")
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return f"Prompt for {version} not found"


def _eval_one(
    item: EvalItem, agent: Any, judge_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Evaluate a single item with the given agent.

    Args:
        item: The evaluation item to process.
        agent: The agent instance to use for evaluation.

    Returns:
        dict[str, Any]: Evaluation result containing item details, agent response,
            and status information.
    """
    try:
        agent_result: AgentResult = agent.run(
            company=item.company, question=item.question
        )
        # LLM-as-a-judge (factual) per-item evaluation alongside inference
        judge = None
        if judge_config and bool(judge_config.get("enabled", True)):
            try:
                judge = _run_llm_judge(
                    question=item.question,
                    expected_answer=str(item.expected_answer or ""),
                    predicted_answer=str(agent_result.answer or ""),
                    judge_config=judge_config,
                    company=item.company,
                )
            except Exception as _:
                judge = None
        return {
            "id": item.item_id,
            "company": item.company,
            "question": item.question,
            "expected_answer": item.expected_answer,
            "answer": agent_result.answer,
            "num_citations": len(agent_result.citations or []),
            "status": "success",
            "judge": judge,
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
            "judge": None,
        }


def _evaluate_in_parallel(
    agent: Any,
    items: list[EvalItem],
    max_workers: int,
    judge_config: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Evaluate multiple items in parallel using ThreadPoolExecutor.

    Args:
        agent: The agent instance to use for evaluation.
        items: List of evaluation items to process.
        max_workers: Maximum number of worker threads to use.

    Returns:
        list[dict[str, Any]]: List of evaluation results for all items.
    """
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {
            executor.submit(_eval_one, item, agent, judge_config): item
            for item in items
        }
        for future in as_completed(future_to_item):
            try:
                result = future.result()
                results.append(result)
                if len(results) % 10 == 0:
                    logger.info(f"Completed {len(results)}/{len(items)} items...")
            except Exception as e:  # pragma: no cover - defensive
                item = future_to_item[future]
                logger.error(f"Failed to evaluate item {item.item_id}: {e}")
                results.append(
                    {
                        "id": item.item_id,
                        "company": item.company,
                        "question": item.question,
                        "expected_answer": item.expected_answer,
                        "answer": f"ERROR: {str(e)}",
                        "num_citations": 0,
                        "status": "error",
                    }
                )
    return results


# ------------------------------
# LLM-as-a-Judge per item
# ------------------------------
def _load_rubric_text() -> str:
    rubric_path = (
        Path(__file__).resolve().parents[2] / "prompts" / "judge" / "rubric_v1.txt"
    )
    try:
        return rubric_path.read_text(encoding="utf-8").strip()
    except Exception:
        return "Judge on factual correctness and groundedness only. Output pass/fail and rationale."


def _run_llm_judge(
    *,
    question: str,
    expected_answer: str,
    predicted_answer: str,
    judge_config: dict[str, Any],
    company: str,
) -> dict[str, Any]:
    """Call an LLM to judge factual correctness of predicted_answer vs expected_answer.

    Returns a dict like: {"pass": bool, "rationale": str}
    """
    model_name = str(judge_config.get("model", "gemini-1.5-pro-latest"))
    temperature = float(judge_config.get("temperature", 0.0))

    import google.generativeai as genai  # type: ignore

    api_key = judge_config.get("google_api_key") or os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set; required for LLM judge calls.")
    genai.configure(api_key=api_key)

    rubric = _load_rubric_text()
    system = (
        f"{rubric}\n\n"
        f"Strictly output a compact JSON object with keys pass (boolean) and rationale (string)."
    )
    prompt = (
        f"System instructions:\n{system}\n\n"
        f"Company: {company}\n"
        f"Question: {question}\n"
        f"Expected answer (ground truth): {expected_answer}\n"
        f"Predicted answer: {predicted_answer}\n\n"
        f"Evaluate factual alignment. Do not nitpick wording."
    )

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": 256,
        },
    )
    text = (getattr(response, "text", None) or "").strip()

    # Best-effort JSON parse; fallback to pass=False
    try:
        data = json.loads(text)
        return {
            "pass": bool(data.get("pass", False)),
            "rationale": str(data.get("rationale", "")),
        }
    except Exception:
        # Try to extract a boolean from text heuristically
        lowered = text.lower()
        is_pass = "pass" in lowered and "fail" not in lowered
        return {"pass": bool(is_pass), "rationale": text[:500]}


def _compute_operational_metrics(results: list[dict[str, Any]]) -> dict[str, float]:
    """Compute operational metrics from evaluation results.

    Args:
        results: List of evaluation result dictionaries.

    Returns:
        dict[str, float]: Dictionary containing total_items, successful_items,
            and success_rate metrics.
    """
    total = float(len(results))
    successes = float(sum(1 for r in results if r.get("status") == "success"))
    success_rate = (successes / total) if total > 0 else 0.0
    # Aggregate LLM-judge metric if present
    judged = [r for r in results if r.get("judge") is not None]
    judge_passes = [
        1.0 if ((r.get("judge") or {}).get("pass") is True) else 0.0 for r in judged
    ]
    judge_rate = (sum(judge_passes) / len(judge_passes)) if judge_passes else 0.0

    return {
        "total_items": total,
        "successful_items": successes,
        "success_rate": success_rate,
        "judge_pass_rate": float(judge_rate),
    }


def _build_genai_eval_df(results: list[dict[str, Any]]):
    """Build a pandas DataFrame for MLflow GenAI evaluation.

    Args:
        results: List of evaluation result dictionaries.

    Returns:
        pandas.DataFrame: DataFrame with inputs, predictions, and ground_truth
            columns formatted for MLflow evaluation.
    """
    # Imported lazily where used to avoid hard dependency when MLflow disabled
    import pandas as pd  # type: ignore

    return pd.DataFrame(
        {
            "inputs": [f"{r['company']} — {r['question']}" for r in results],
            "predictions": [r["answer"] for r in results],
            "ground_truth": [r["expected_answer"] for r in results],
        }
    )


def _log_mlflow(
    mlflow: Any,
    *,
    version: str,
    dataset: Path,
    config: dict[str, Any],
    run_name: str,
    results: list[dict[str, Any]],
    metrics: dict[str, float],
) -> None:
    """Log evaluation results and artifacts to MLflow.

    Args:
        mlflow: MLflow module instance.
        version: Agent version string.
        dataset: Path to the dataset used for evaluation.
        config: Configuration dictionary containing agent and evaluation settings.
        run_name: Name for the MLflow run.
        results: List of evaluation result dictionaries.
        metrics: Dictionary of computed operational metrics.
    """
    with mlflow.start_run(run_name=run_name):  # type: ignore[attr-defined]
        # Params
        mlflow.log_params(  # type: ignore[attr-defined]
            {
                "version": version,
                "dataset": str(dataset),
                "model": str(config.get("model", "")),
                "steps": int(config.get("steps", 0)),
                "max_workers": int(config.get("max_workers", 0) or 0),
            }
        )

        # Operational metrics
        mlflow.log_metric("success_rate", float(metrics["success_rate"]))  # type: ignore[attr-defined]
        mlflow.log_metric("total_items", float(metrics["total_items"]))  # type: ignore[attr-defined]
        mlflow.log_metric("successful_items", float(metrics["successful_items"]))  # type: ignore[attr-defined]
        # LLM judge metric
        mlflow.log_metric("judge_pass_rate", float(metrics.get("judge_pass_rate", 0.0)))  # type: ignore[attr-defined]

        # GenAI evaluation (heuristic metrics, optional judge if configured)
        try:
            eval_df = _build_genai_eval_df(results)
            eval_result = mlflow.evaluate(
                data=eval_df,
                predictions="predictions",
                targets="ground_truth",
                model_type="question-answering",
                evaluators="default",
                extra_metrics=[mlflow.metrics.genai.answer_similarity()],
            )
            for key, value in (getattr(eval_result, "metrics", {}) or {}).items():
                try:
                    mlflow.log_metric(f"eval.{key}", float(value))  # type: ignore[attr-defined]
                except Exception:  # pragma: no cover - ignore non-numeric
                    pass

            # Persist evaluation dataframe
            genai_eval_path = MLFLOW_OUTPUT_DIR / f"genai_eval_{version}.csv"
            genai_eval_path.parent.mkdir(parents=True, exist_ok=True)
            eval_df.to_csv(genai_eval_path, index=False)
            mlflow.log_artifact(str(genai_eval_path))  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - optional
            logger.warning(f"GenAI evaluation skipped: {exc}")

        # Prompt artifact
        prompt_content = _get_agent_prompt(version)
        prompt_path = MLFLOW_OUTPUT_DIR / f"prompt_{version}.txt"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt_content, encoding="utf-8")
        mlflow.log_artifact(str(prompt_path))  # type: ignore[attr-defined]

        # Results table artifact
        try:
            import pandas as pd  # type: ignore

            df = pd.DataFrame(results)
            dataset_table_path = MLFLOW_OUTPUT_DIR / f"evaluation_dataset_{version}.csv"
            df.to_csv(dataset_table_path, index=False)
            mlflow.log_artifact(str(dataset_table_path))  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover
            logger.warning(f"Failed to log dataset table artifact: {exc}")

        # Detailed JSONL artifact
        results_path = MLFLOW_OUTPUT_DIR / f"results_{version}_{dataset.stem}.jsonl"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with results_path.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        mlflow.log_artifact(str(results_path))  # type: ignore[attr-defined]


def run_evaluation(
    dataset_path: str | None = None,
    version: str = "v001",
    config: dict[str, Any] | None = None,
    run_name: str | None = None,
) -> None:
    """Run evaluation for a specific agent version on dataset(s).

    This function orchestrates the entire evaluation process:
    1. Loads the dataset(s) and creates evaluation items
    2. Initializes the specified agent
    3. Runs parallel evaluation of all items
    4. Computes operational metrics
    5. Logs results and artifacts to MLflow (if enabled)

    Args:
        dataset_path: Optional path to a specific dataset file for evaluation.
                      If None, loads from both hardcoded datasets.
        version: Agent version to evaluate (e.g., 'v001', 'v002').
        config: Configuration dictionary containing agent and MLflow settings.
        run_name: Optional custom name for the MLflow run.
            If not provided, uses the version or config default.

    Raises:
        FileNotFoundError: If a specific dataset file is provided but doesn't exist.
        ValueError: If the specified agent version is not supported.
    """
    if config is None:
        config = {}

    # Handle dataset loading
    if dataset_path is not None:
        dataset = Path(dataset_path)
        if not dataset.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset}")
        items = _load_eval_items(dataset)
    else:
        # Load from both hardcoded datasets
        items = _load_eval_items()
        dataset = Path("combined_datasets")  # Placeholder for MLflow logging

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

            mlflow = _mlflow
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            if experiment_name:
                mlflow.set_experiment(experiment_name)
        except Exception as exc:  # pragma: no cover - optional integration
            logger.warning(f"MLflow disabled due to import/config error: {exc}")
            mlflow = None

    agent = agent_cls(config)
    logger.info(f"Processing {len(items)} items with {version} agent...")

    max_workers = min(8, len(items))
    # Expose for logging later
    config = {**config, "max_workers": max_workers}

    judge_cfg = dict(config.get("judge", {})) if isinstance(config, dict) else {}
    results = _evaluate_in_parallel(agent, items, max_workers, judge_cfg)

    # Calculate basic metrics
    metrics = _compute_operational_metrics(results)

    # Log to MLflow
    if mlflow is not None:
        _log_mlflow(
            mlflow,
            version=version,
            dataset=dataset,
            config=config,
            run_name=effective_run_name,
            results=results,
            metrics=metrics,
        )

    # Console summary via logging
    logger.info(f"Completed {len(results)} examples")
    logger.info(f"Success rate: {metrics['success_rate']:.1%}")
    successes = int(metrics["successful_items"]) if metrics else 0
    if successes:
        logger.info(f"Successful evaluations: {successes}")
    failures = (
        int(metrics["total_items"] - metrics["successful_items"]) if metrics else 0
    )
    if failures > 0:
        logger.info(f"Failed evaluations: {failures}")
