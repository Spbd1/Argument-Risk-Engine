from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class EvaluationRunRequest(BaseModel):
    benchmark_path: str | None = None


class EvaluationResponse(BaseModel):
    items: int
    metrics: dict[str, float]
    errors: dict[str, list[dict[str, Any]]]
    false_positives: list[dict[str, Any]]
    false_negatives: list[dict[str, Any]]
    evidence_span_misses: list[dict[str, Any]]
    analyses: list[dict[str, Any]]
    disclaimer: str
