from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from argument_risk_engine.review.models import ReviewFeedback, ReviewItem, validate_review_item


def append_review_item(path: Path, item: ReviewItem) -> ReviewItem:
    data = item.model_dump()
    validate_review_item(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")
    return item


def read_review_items(path: Path) -> list[ReviewItem]:
    if not path.exists():
        return []
    items: list[ReviewItem] = []
    for _line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        data = json.loads(line)
        validate_review_item(data)
        items.append(ReviewItem(**data))
    return items


def review_summary(path: Path) -> dict[str, Any]:
    items = read_review_items(path)
    by_decision: dict[str, int] = {}
    corrected_label_counts: dict[str, int] = {}
    for item in items:
        by_decision[item.reviewer_decision] = by_decision.get(item.reviewer_decision, 0) + 1
        for label in item.corrected_labels:
            corrected_label_counts[label] = corrected_label_counts.get(label, 0) + 1
    return {
        "total_reviews": len(items),
        "by_decision": by_decision,
        "corrected_label_counts": corrected_label_counts,
        "store_path": str(path),
    }


def append_feedback(path: Path, feedback: ReviewFeedback) -> None:
    """Legacy adapter that records old feedback payloads in the append-only review store."""

    item = ReviewItem(
        text_id=feedback.analysis_id,
        claim_id=feedback.taxonomy_id or "legacy_feedback",
        claim_text="",
        predicted_risks=[{"taxonomy_id": feedback.taxonomy_id}] if feedback.taxonomy_id else [],
        reviewer_decision=_legacy_decision(feedback.decision),
        reviewer_notes=feedback.notes,
    )
    append_review_item(path, item)


def _legacy_decision(decision: str) -> str:
    return {"partial": "partially_correct"}.get(decision, decision)
