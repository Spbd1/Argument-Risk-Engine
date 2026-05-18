from pathlib import Path

from argument_risk_engine.evaluation.runner import run_evaluation

if __name__ == "__main__":
    result = run_evaluation(Path(__file__).resolve().parents[1] / "data/benchmarks/mini_eval_set.jsonl")
    print(f"Evaluated {result['items']} items")
