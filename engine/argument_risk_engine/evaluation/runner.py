from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from argument_risk_engine.analyzer import analyze_text
from argument_risk_engine.evaluation.metrics import compute_metrics

DISCLAIMER = (
    "MVP evaluation metrics are operational QA indicators for this benchmark only; "
    "they do not establish scientific or clinical validation."
)


def run_evaluation(path: Path | str) -> dict[str, Any]:
    rows = load_benchmark(path)
    analyses = [analyze_text(row.get("text", "")) for row in rows]
    metrics = compute_metrics(rows, analyses)
    errors = collect_errors(rows, analyses)
    return {
        "items": len(rows),
        "metrics": metrics,
        "errors": errors,
        "false_positives": errors["false_positives"],
        "false_negatives": errors["false_negatives"],
        "evidence_span_misses": errors["evidence_span_misses"],
        "analyses": analyses,
        "disclaimer": DISCLAIMER,
    }


def load_benchmark(path: Path | str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def collect_errors(rows: list[dict[str, Any]], analyses: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    false_positives: list[dict[str, Any]] = []
    false_negatives: list[dict[str, Any]] = []
    evidence_span_misses: list[dict[str, Any]] = []
    for row, analysis in zip(rows, analyses, strict=False):
        row_id = str(row.get("id") or row.get("text_id") or "unknown")
        gold_labels = {str(label) for label in row.get("gold_labels", row.get("expected", []))}
        predicted_labels = {str(risk.get("risk_id") or risk.get("label") or "") for risk in analysis.get("risks", []) if risk}
        for label in sorted(predicted_labels - gold_labels):
            false_positives.append({"id": row_id, "label": label, "text": row.get("text", "")})
        for label in sorted(gold_labels - predicted_labels):
            false_negatives.append({"id": row_id, "label": label, "text": row.get("text", "")})
        gold_spans = [str(span) for span in row.get("gold_evidence_spans", [])]
        if gold_spans:
            predicted_spans = [str(risk.get("evidence_span") or "") for risk in analysis.get("risks", [])]
            if not any(pred == gold for pred in predicted_spans for gold in gold_spans):
                evidence_span_misses.append({"id": row_id, "gold_spans": gold_spans, "predicted_spans": predicted_spans})
    return {
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "evidence_span_misses": evidence_span_misses,
    }
