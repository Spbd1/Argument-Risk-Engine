from __future__ import annotations

from argument_risk_engine.review.models import ReviewFeedback

from backend.app.schemas.review import ReviewItemRequest
from backend.app.services.review_service import (
    create_review_item,
    get_review_summary,
    list_review_items,
    record_feedback,
)
from fastapi import APIRouter

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/items")
def items() -> list[dict[str, object]]:
    return list_review_items()


@router.post("/items")
def create_item(payload: ReviewItemRequest) -> dict[str, object]:
    return create_review_item(payload)


@router.get("/summary")
def summary() -> dict[str, object]:
    return get_review_summary()


@router.post("/feedback")
def feedback(payload: ReviewFeedback) -> dict[str, str]:
    return record_feedback(payload)
