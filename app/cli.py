import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from app.agents.base import AgentResult
from app.agents.v001_minimal import AgentV001
from app.agents.v002_research import AgentV002
from app.agents.v003_rag import AgentV003
from app.agents.v004_deep_planner import AgentV004
from app.config import load_config
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

    # Common params
    parser.add_argument(
        "--dataset", type=str, default="", help="Path to evaluation dataset (JSONL)"
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


def main() -> int:
    # Load environment variables from .env if present
    load_dotenv()

    args = parse_args()
    overrides = parse_overrides(args.set)
    cfg = load_config(args.version, args.profile, overrides)
    setup_logging(cfg.get("log_level", "INFO"))

    # Mode dispatch (stubs for now)
    if args.ingest:
        print("[INGEST] RAG ingestion requested. Implement in app.tools.ingestion.")
        return 0

    if args.eval:
        print("[EVAL] Batch evaluation requested. Implement in app.evaluation.runner.")
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
