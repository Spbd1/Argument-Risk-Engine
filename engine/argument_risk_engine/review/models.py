from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

ReviewDecision = Literal[
    "correct",
    "incorrect",
    "partially_correct",
    "insufficient_evidence",
    "unclear",
]

VALID_REVIEW_DECISIONS = {
    "correct",
    "incorrect",
    "partially_correct",
    "insufficient_evidence",
    "unclear",
}


class ReviewValidationError(ValueError):
    """Raised when a review record is incomplete or invalid."""


class ReviewItem(BaseModel):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid4().hex[:12]}")
    text_id: str
    claim_id: str
    claim_text: str
    predicted_risks: list[dict[str, Any]] = Field(default_factory=list)
    reviewer_decision: ReviewDecision
    corrected_labels: list[str] = Field(default_factory=list)
    corrected_evidence_spans: list[str] = Field(default_factory=list)
    reviewer_notes: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate_item(self) -> None:
        validate_review_item(self.model_dump())


class ReviewFeedback(BaseModel):
    """Legacy feedback shape kept for older dashboard clients."""

    analysis_id: str
    taxonomy_id: str | None = None
    decision: str
    notes: str = ""


def validate_review_item(data: dict[str, Any]) -> None:
    required_strings = ["review_id", "text_id", "claim_id", "claim_text", "reviewer_decision", "created_at"]
    missing = [field for field in required_strings if not str(data.get(field) or "").strip()]
    if missing:
        raise ReviewValidationError(f"Review item missing required fields: {', '.join(missing)}")
    decision = str(data.get("reviewer_decision") or "")
    if decision not in VALID_REVIEW_DECISIONS:
        raise ReviewValidationError(f"Unsupported reviewer_decision: {decision}")
    for list_field in ("predicted_risks", "corrected_labels", "corrected_evidence_spans"):
        if not isinstance(data.get(list_field, []), list):
            raise ReviewValidationError(f"{list_field} must be a list")
    try:
        datetime.fromisoformat(str(data["created_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReviewValidationError("created_at must be an ISO-8601 timestamp") from exc
