from argument_risk_engine.review.models import ReviewFeedback
from argument_risk_engine.review.store import append_feedback

from backend.app.core.paths import REVIEW_STORE_PATH


def record_feedback(feedback: ReviewFeedback) -> dict[str, str]:
    append_feedback(REVIEW_STORE_PATH, feedback)
    return {"status": "recorded"}
