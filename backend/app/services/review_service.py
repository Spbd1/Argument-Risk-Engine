from __future__ import annotations

from argument_risk_engine.review.models import ReviewFeedback, ReviewItem
from argument_risk_engine.review.store import (
    append_feedback,
    append_review_item,
    read_review_items,
    review_summary,
)

from backend.app.core.paths import REVIEW_STORE_PATH
from backend.app.schemas.review import ReviewItemRequest


def list_review_items() -> list[dict[str, object]]:
    return [item.model_dump() for item in read_review_items(REVIEW_STORE_PATH)]


def create_review_item(payload: ReviewItemRequest | ReviewItem) -> dict[str, object]:
    if isinstance(payload, ReviewItem):
        item = payload
    else:
        data = payload.model_dump()
        if not data.get("review_id"):
            data.pop("review_id", None)
        item = ReviewItem(**data)
    return append_review_item(REVIEW_STORE_PATH, item).model_dump()


def get_review_summary() -> dict[str, object]:
    return review_summary(REVIEW_STORE_PATH)


def record_feedback(feedback: ReviewFeedback) -> dict[str, str]:
    append_feedback(REVIEW_STORE_PATH, feedback)
    return {"status": "recorded"}
