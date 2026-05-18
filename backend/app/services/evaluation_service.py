from argument_risk_engine.evaluation.runner import run_evaluation

from backend.app.core.paths import DATA_DIR


def evaluate() -> dict[str, object]:
    return run_evaluation(DATA_DIR / "benchmarks" / "mini_eval_set.jsonl")
