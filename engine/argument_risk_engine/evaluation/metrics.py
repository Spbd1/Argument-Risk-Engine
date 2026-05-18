from __future__ import annotations

from typing import Any


def precision(tp: int, fp: int) -> float:
    return tp / (tp + fp) if tp + fp else 0.0


def recall(tp: int, fn: int) -> float:
    return tp / (tp + fn) if tp + fn else 0.0


def f1_score(label_precision: float, label_recall: float) -> float:
    return 2 * label_precision * label_recall / (label_precision + label_recall) if label_precision + label_recall else 0.0


def partial_span_match(predicted: str, gold: str) -> bool:
    predicted_norm = predicted.strip().lower()
    gold_norm = gold.strip().lower()
    return bool(predicted_norm and gold_norm and (predicted_norm in gold_norm or gold_norm in predicted_norm))


def compute_metrics(rows: list[dict[str, Any]], analyses: list[dict[str, Any]]) -> dict[str, float]:
    tp = fp = fn = 0
    exact_matches = partial_matches = span_cases = 0
    review_count = over_classified = no_finding = 0

    for row, analysis in zip(rows, analyses, strict=False):
        gold_labels = set(_gold_labels(row))
        predicted_labels = set(_predicted_labels(analysis))
        tp += len(predicted_labels & gold_labels)
        fp += len(predicted_labels - gold_labels)
        fn += len(gold_labels - predicted_labels)

        if analysis.get("needs_human_review"):
            review_count += 1
        if len(predicted_labels) > len(gold_labels):
            over_classified += 1
        if not predicted_labels:
            no_finding += 1

        gold_spans = _gold_spans(row)
        predicted_spans = _predicted_spans(analysis)
        if gold_spans:
            span_cases += 1
            if any(pred == gold for pred in predicted_spans for gold in gold_spans):
                exact_matches += 1
            if any(partial_span_match(pred, gold) for pred in predicted_spans for gold in gold_spans):
                partial_matches += 1

    label_precision = precision(tp, fp)
    label_recall = recall(tp, fn)
    total = len(rows)
    return {
        "label_precision": round(label_precision, 4),
        "label_recall": round(label_recall, 4),
        "label_f1": round(f1_score(label_precision, label_recall), 4),
        "false_positive_rate": round(fp / (fp + tp) if fp + tp else 0.0, 4),
        "evidence_span_exact_match": round(exact_matches / span_cases if span_cases else 0.0, 4),
        "evidence_span_partial_match": round(partial_matches / span_cases if span_cases else 0.0, 4),
        "human_review_rate": round(review_count / total if total else 0.0, 4),
        "over_classification_rate": round(over_classified / total if total else 0.0, 4),
        "no_finding_rate": round(no_finding / total if total else 0.0, 4),
    }


def _gold_labels(row: dict[str, Any]) -> list[str]:
    return [str(label) for label in row.get("gold_labels", row.get("expected", []))]


def _gold_spans(row: dict[str, Any]) -> list[str]:
    return [str(span) for span in row.get("gold_evidence_spans", [])]


def _predicted_labels(analysis: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for risk in analysis.get("risks", []):
        labels.append(str(risk.get("risk_id") or risk.get("label") or ""))
    return [label for label in labels if label]


def _predicted_spans(analysis: dict[str, Any]) -> list[str]:
    return [str(risk.get("evidence_span") or "") for risk in analysis.get("risks", []) if risk.get("evidence_span")]
