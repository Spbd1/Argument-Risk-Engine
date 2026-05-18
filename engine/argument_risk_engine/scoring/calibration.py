from __future__ import annotations

from dataclasses import dataclass


RISK_LEVEL_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (0.75, "severe"),
    (0.50, "high"),
    (0.25, "moderate"),
    (0.00, "low"),
)

SEVERITY_WEIGHTS: dict[str, float] = {"low": 0.35, "medium": 0.68, "high": 1.0}


@dataclass(frozen=True)
class CalibrationProfile:
    minimum_confidence: float = 0.45
    non_exact_evidence_review_threshold: float = 0.01
    healthy_suppressor_penalty: float = 0.18
    high_false_positive_minimum_evidence: float = 0.75
    high_false_positive_minimum_confidence: float = 0.62
    contextual_isolated_cap: float = 0.49
    short_claim_high_confidence_limit: int = 2
    short_claim_char_limit: int = 160


def conservative_threshold() -> float:
    return 0.5


def default_calibration() -> CalibrationProfile:
    return CalibrationProfile()


def severity_weight(severity: str) -> float:
    return SEVERITY_WEIGHTS.get(str(severity or "").lower(), SEVERITY_WEIGHTS["low"])


def risk_level(score: float) -> str:
    bounded = max(0.0, min(1.0, float(score or 0.0)))
    for threshold, label in RISK_LEVEL_THRESHOLDS:
        if bounded >= threshold:
            return label
    return "low"
