import argparse
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.agents.base import AgentResult
from app.agents.v001_minimal import AgentV001
from app.agents.v002_research import AgentV002
from app.agents.v003_rag import AgentV003
from app.agents.v004_deep_planner import AgentV004
from app.config import load_config
from app.evaluation.runner import run_evaluation, run_evaluation_on_combined_datasets
from app.logging.setup import setup_logging

AGENT_BY_VERSION = {
    "v001": AgentV001,
    "v002": AgentV002,
    "v003": AgentV003,
    "v004": AgentV004,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic system CLI (V001–V004)")
    parser.add_argument(
        "--version", choices=["v001", "v002", "v003", "v004"], default="v001"
    )
    parser.add_argument("--company", type=str, default="", help="Target company name")
    parser.add_argument("--question", type=str, default="", help="User question")

    # Modes
    parser.add_argument(
        "--ingest", action="store_true", help="Run RAG ingestion (V003)"
    )
    parser.add_argument("--rag", action="store_true", help="Use RAG mode (V003)")
    parser.add_argument(
        "--deep", action="store_true", help="Use deep planning mode (V004)"
    )
    parser.add_argument(
        "--eval", action="store_true", help="Run evaluation on a dataset"
    )
    parser.add_argument(
        "--eval-combined",
        action="store_true",
        help="Run evaluation on combined datasets (original + transformed)",
    )
    parser.add_argument(
        "--eval-profile",
        type=str,
        default="",
        help="Use evaluation profile from app/config/evaluation_profiles/",
    )

    # Common params
    parser.add_argument(
        "--dataset", type=str, default="", help="Path to evaluation dataset (JSONL)"
    )
    parser.add_argument(
        "--judge-enabled",
        action="store_true",
        help="Enable LLM-as-judge per-item evaluation",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default="gemini-1.5-pro-latest",
        help="Judge model to use",
    )
    parser.add_argument(
        "--judge-temperature", type=float, default=0.0, help="Judge model temperature"
    )
    parser.add_argument("--steps", type=int, default=8, help="Default steps (V002)")
    parser.add_argument("--run-name", type=str, default="", help="MLflow run name")
    parser.add_argument("--profile", type=str, default=os.getenv("ADK_PROFILE", "dev"))

    # V004 planning
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--max-questions", type=int, default=3)
    parser.add_argument(
        "--assume-missing",
        type=str,
        default="conservative",
        choices=["conservative", "optimistic", "none"],
    )
    parser.add_argument("--explain-plan", action="store_true")

    # Retriever knobs (V003)
    parser.add_argument("--retriever.top_k", type=int, default=8)
    parser.add_argument("--retriever.min_score", type=float, default=0.3)

    # Simple override mechanism: --set key=value pairs
    parser.add_argument(
        "--set", nargs="*", default=[], help="Override config values: key=value"
    )

    return parser.parse_args()


def parse_overrides(pairs: list[str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        overrides[key.strip()] = value.strip()
    return overrides


def _load_evaluation_config(profile_name: str) -> dict[str, Any]:
    """Load evaluation configuration from YAML files.

    Args:
        profile_name: Name of evaluation profile (e.g., 'quick', 'full_with_judge')
                     If empty, loads default evaluation.yaml

    Returns:
        dict: Evaluation configuration
    """
    import yaml

    # Try multiple possible paths for the config files
    possible_paths = [
        # From project root (when running poetry run adk)
        Path.cwd() / "app" / "config" / "evaluation.yaml",
        # From CLI file location
        Path(__file__).resolve().parents[1] / "config" / "evaluation.yaml",
        # From CLI file location (alternative)
        Path(__file__).resolve().parents[2] / "app" / "config" / "evaluation.yaml",
    ]

    base_config_path = None
    for path in possible_paths:
        if path.exists():
            base_config_path = path
            break

    if not base_config_path:
        raise FileNotFoundError(
            f"Base evaluation config not found. Tried: {[str(p) for p in possible_paths]}"
        )

    with open(base_config_path, "r") as f:
        base_config = yaml.safe_load(f)

    # Load profile if specified
    if profile_name:
        # Determine the evaluation_profiles directory based on where we found the base config
        if "app/config" in str(base_config_path):
            profiles_dir = base_config_path.parent / "evaluation_profiles"
        else:
            profiles_dir = Path.cwd() / "app" / "config" / "evaluation_profiles"

        profile_path = profiles_dir / f"{profile_name}.yaml"

        if not profile_path.exists():
            raise FileNotFoundError(f"Evaluation profile not found: {profile_path}")

        with open(profile_path, "r") as f:
            profile_config = yaml.safe_load(f)

        # Merge profile with base config (profile overrides base)
        _merge_configs(base_config, profile_config)

    return base_config


def _merge_configs(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Recursively merge override config into base config."""
    for key, value in override.items():
        if key == "_extends":
            continue  # Skip extends directive
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_configs(base[key], value)
        else:
            base[key] = value


def main() -> int:
    # Load environment variables from project root .env explicitly
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env", override=True)

    args = parse_args()
    overrides = parse_overrides(args.set)
    cfg = load_config(args.version, args.profile, overrides)
    setup_logging(cfg.get("log_level", "INFO"))

    # Mode dispatch (stubs for now)
    if args.ingest:
        print("[INGEST] RAG ingestion requested. Implement in app.tools.ingestion.")
        return 0

    if args.eval:
        if not args.dataset:
            print("[EVAL] --dataset path is required for evaluation", file=sys.stderr)
            return 1

        # Add judge configuration if enabled
        if args.judge_enabled:
            cfg["judge"] = {
                "enabled": True,
                "model": args.judge_model,
                "temperature": args.judge_temperature,
            }

        run_evaluation(
            dataset_path=args.dataset,
            version=args.version,
            config=cfg,
            run_name=args.run_name or None,
        )
        return 0

    if args.eval_combined or args.eval_profile:
        # Load evaluation configuration
        eval_config = _load_evaluation_config(args.eval_profile)

        # Merge with CLI overrides
        if args.judge_enabled:
            eval_config["judge"]["enabled"] = True
            eval_config["judge"]["model"] = args.judge_model
            eval_config["judge"]["temperature"] = args.judge_temperature

        if args.run_name:
            eval_config["mlflow"]["run_name"] = args.run_name

        # Determine which evaluation function to call
        if eval_config["datasets"]["use_combined"]:
            run_evaluation_on_combined_datasets(
                version=eval_config["agent"]["version"],
                config=eval_config,
                run_name=eval_config["mlflow"]["run_name"] or None,
            )
        else:
            dataset_path = (
                eval_config["datasets"]["custom"] or eval_config["datasets"]["original"]
            )
            run_evaluation(
                dataset_path=dataset_path,
                version=eval_config["agent"]["version"],
                config=eval_config,
                run_name=eval_config["mlflow"]["run_name"] or None,
            )
        return 0

    # Interactive run (prompt for inputs if not provided)
    if not args.company:
        args.company = input("Company: ").strip()
    if not args.question:
        args.question = input("Question: ").strip()
    agent_cls = AGENT_BY_VERSION.get(args.version)
    if not agent_cls:
        print(f"Unsupported version: {args.version}", file=sys.stderr)
        return 1

    agent = agent_cls(cfg)
    result: AgentResult = agent.run(company=args.company, question=args.question)

    print("\n=== Answer ===")
    print(result.answer)
    if result.citations:
        print("\nCitations:")
        for idx, cit in enumerate(result.citations, 1):
            print(f"[{idx}] {cit}")
    if result.assumptions:
        print("\nAssumptions:")
        for a in result.assumptions:
            print(f"- {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
