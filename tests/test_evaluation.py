from __future__ import annotations

from argument_risk_engine.evaluation.metrics import compute_metrics
from argument_risk_engine.evaluation.runner import run_evaluation


def test_evaluation_runner(tmp_path):
    path = tmp_path / "eval.jsonl"
    path.write_text('{"id":"sample_001","text":"They are vermin.","gold_labels":["dehumanizing_language"],"gold_evidence_spans":["vermin"],"difficulty":"easy","notes":"smoke"}\n')
    result = run_evaluation(path)

    assert result["items"] == 1
    assert "label_precision" in result["metrics"]
    assert "do not establish scientific" in result["disclaimer"]


def test_metrics_include_required_operational_rates():
    rows = [{"gold_labels": ["a"], "gold_evidence_spans": ["abc"]}]
    analyses = [{"risks": [{"risk_id": "a", "evidence_span": "abc"}], "needs_human_review": True}]

    metrics = compute_metrics(rows, analyses)

    assert metrics == {
        "label_precision": 1.0,
        "label_recall": 1.0,
        "label_f1": 1.0,
        "false_positive_rate": 0.0,
        "evidence_span_exact_match": 1.0,
        "evidence_span_partial_match": 1.0,
        "human_review_rate": 1.0,
        "over_classification_rate": 0.0,
        "no_finding_rate": 0.0,
    }
