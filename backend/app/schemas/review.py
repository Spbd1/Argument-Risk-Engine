from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReviewItemRequest(BaseModel):
    review_id: str | None = None
    text_id: str
    claim_id: str
    claim_text: str
    predicted_risks: list[dict[str, Any]] = Field(default_factory=list)
    reviewer_decision: str
    corrected_labels: list[str] = Field(default_factory=list)
    corrected_evidence_spans: list[str] = Field(default_factory=list)
    reviewer_notes: str = ""


class ReviewItemResponse(BaseModel):
    review_id: str
    text_id: str
    claim_id: str
    claim_text: str
    predicted_risks: list[dict[str, Any]]
    reviewer_decision: str
    corrected_labels: list[str]
    corrected_evidence_spans: list[str]
    reviewer_notes: str
    created_at: str


class ReviewSummaryResponse(BaseModel):
    total_reviews: int
    by_decision: dict[str, int]
    corrected_label_counts: dict[str, int]
    store_path: str
