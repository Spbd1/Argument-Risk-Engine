from argument_risk_engine.review.models import ReviewFeedback

from backend.app.services.review_service import record_feedback
from fastapi import APIRouter

router = APIRouter(prefix="/review", tags=["review"])

@router.post("/feedback")
def feedback(payload: ReviewFeedback) -> dict[str, str]:
    return record_feedback(payload)
