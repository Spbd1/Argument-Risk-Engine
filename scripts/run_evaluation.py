from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT))

from argument_risk_engine.evaluation.runner import run_evaluation  # noqa: E402,I001


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Argument Risk Engine mini benchmark.")
    parser.add_argument(
        "benchmark",
        nargs="?",
        default=str(ROOT / "data/benchmarks/mini_eval_set.jsonl"),
        help="Path to a JSONL benchmark file.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full evaluation payload as JSON.")
    args = parser.parse_args()

    result = run_evaluation(Path(args.benchmark))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Evaluated {result['items']} items")
        for name, value in result["metrics"].items():
            print(f"{name}: {value}")
        print(result["disclaimer"])
