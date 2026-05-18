from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from argument_risk_engine.evaluation.runner import run_evaluation

from backend.app.core.paths import DATA_DIR

BENCHMARK_PATH = DATA_DIR / "benchmarks" / "mini_eval_set.jsonl"
EVALUATION_RESULT_PATH = DATA_DIR / "evaluation" / "last_evaluation.json"


def evaluate(benchmark_path: str | None = None) -> dict[str, Any]:
    path = Path(benchmark_path) if benchmark_path else BENCHMARK_PATH
    result = run_evaluation(path)
    EVALUATION_RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVALUATION_RESULT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def evaluation_summary() -> dict[str, Any]:
    result = _load_or_run()
    return {
        "items": result.get("items", 0),
        "metrics": result.get("metrics", {}),
        "disclaimer": result.get("disclaimer", ""),
    }


def evaluation_errors() -> dict[str, Any]:
    result = _load_or_run()
    return result.get("errors", {"false_positives": [], "false_negatives": [], "evidence_span_misses": []})


def _load_or_run() -> dict[str, Any]:
    if EVALUATION_RESULT_PATH.exists():
        return json.loads(EVALUATION_RESULT_PATH.read_text(encoding="utf-8"))
    return evaluate()
