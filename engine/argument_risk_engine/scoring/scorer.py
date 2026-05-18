from __future__ import annotations

SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}


def score_risk(severity: str, confidence: float) -> float:
    return round(SEVERITY_WEIGHT.get(severity, 1) * confidence / 3, 3)
