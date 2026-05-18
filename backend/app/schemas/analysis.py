from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1)
    mode: str = "deterministic_baseline"
    model_provider_id: str = "deterministic_baseline"
    top_k: int = 8
    include_healthy_patterns: bool = True
    max_risks_per_claim: int = 3
    allow_deterministic_fallback: bool = True
    include_retrieval_diagnostics: bool = False


class DetectedRisk(BaseModel):
    risk_id: str
    category: str
    label: str
    severity: str
    confidence: float
    risk_score: float
    risk_level: str
    evidence_span: str
    evidence_start_char: int
    evidence_end_char: int
    explanation: str
    false_positive_warning: str
    needs_human_review: bool


class AnalyzedClaim(BaseModel):
    claim_id: str
    text: str
    claim_type: str
    start_char: int
    end_char: int
    detected_risks: list[DetectedRisk]
    healthy_patterns: list[dict[str, Any]]
    warnings: list[str]
    retrieval_diagnostics: dict[str, Any]


class AnalysisResponse(BaseModel):
    text_id: str
    mode: str
    model_provider_id: str
    model_name: str
    llm_used: bool
    deterministic_fallback_used: bool
    claims: list[AnalyzedClaim]
    overall_risk_score: float
    risk_level: str
    needs_human_review: bool
    warnings: list[str]
