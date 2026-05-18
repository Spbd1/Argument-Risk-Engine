from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from argument_risk_engine.scoring.calibration import (
    CalibrationProfile,
    default_calibration,
    risk_level,
    severity_weight,
)

LEGACY_SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}


@dataclass(frozen=True)
class ScoredRisk:
    risk_score: float
    risk_level: str
    suppressed: bool = False
    needs_human_review: bool = False
    warning: str = ""


def score_risk(
    severity: str,
    confidence: float,
    *,
    taxonomy_match: float | None = None,
    evidence_strength: float | None = None,
    classifier_confidence: float | None = None,
    consistency_check: float = 1.0,
    claim_type_compatibility: float = 1.0,
) -> float:
    """Score a risk.

    Positional-only legacy calls keep the original severity/confidence behavior.
    Keyword component calls use the end-to-end analyzer formula.
    """

    if taxonomy_match is None and evidence_strength is None and classifier_confidence is None:
        return round(LEGACY_SEVERITY_WEIGHT.get(str(severity), 1) * float(confidence) / 3, 3)

    return calculate_risk_score(
        taxonomy_match=1.0 if taxonomy_match is None else taxonomy_match,
        evidence_strength=1.0 if evidence_strength is None else evidence_strength,
        classifier_confidence=float(confidence if classifier_confidence is None else classifier_confidence),
        severity_weight_value=severity_weight(severity),
        consistency_check=consistency_check,
        claim_type_compatibility=claim_type_compatibility,
    )


def calculate_risk_score(
    *,
    taxonomy_match: float,
    evidence_strength: float,
    classifier_confidence: float,
    severity_weight_value: float,
    consistency_check: float,
    claim_type_compatibility: float,
) -> float:
    score = (
        0.30 * _bounded(taxonomy_match)
        + 0.25 * _bounded(evidence_strength)
        + 0.20 * _bounded(classifier_confidence)
        + 0.10 * _bounded(severity_weight_value)
        + 0.10 * _bounded(consistency_check)
        + 0.05 * _bounded(claim_type_compatibility)
    )
    return round(_bounded(score), 3)


def score_classification(
    classification: dict[str, Any],
    *,
    entry: Any | None = None,
    candidate: Any | None = None,
    claim_text: str = "",
    has_context: bool = False,
    high_confidence_risk_count: int = 0,
    calibration: CalibrationProfile | None = None,
) -> ScoredRisk:
    """Apply the analyzer scoring formula and false-positive guards."""

    profile = calibration or default_calibration()
    confidence = _bounded(float(classification.get("confidence", 0.0) or 0.0))
    if confidence < profile.minimum_confidence:
        return ScoredRisk(0.0, "low", suppressed=True, warning="Excluded because classifier confidence is below 0.45.")

    evidence = str(classification.get("evidence_span", "") or "")
    if not evidence:
        return ScoredRisk(0.0, "low", suppressed=True, warning="Suppressed because no evidence span was provided.")

    exact = bool(classification.get("evidence_exact", True))
    needs_review = not exact
    warnings: list[str] = []
    if not exact:
        warnings.append("Evidence span was not an exact text match; human review recommended.")

    taxonomy_match = _taxonomy_match(candidate, classification)
    evidence_strength = _evidence_strength(classification, exact=exact)
    consistency = _consistency_check(entry, classification, has_context=has_context)
    compatibility = _claim_type_compatibility(entry, str(classification.get("claim_type", "") or ""))

    fp_sensitivity = str(getattr(entry, "false_positive_sensitivity", "medium") or "medium")
    requires_context = bool(getattr(entry, "requires_context", False)) or str(getattr(entry, "detection_level", "")) in {"contextual", "discourse", "cross_claim"}
    if fp_sensitivity == "high" and (evidence_strength < profile.high_false_positive_minimum_evidence or confidence < profile.high_false_positive_minimum_confidence):
        return ScoredRisk(0.0, "low", suppressed=True, warning="Suppressed because high false-positive sensitivity requires stronger evidence.")

    score = score_risk(
        str(classification.get("severity", getattr(getattr(entry, "severity", None), "value", "low")) or "low"),
        confidence,
        taxonomy_match=taxonomy_match,
        evidence_strength=evidence_strength,
        classifier_confidence=confidence,
        consistency_check=consistency,
        claim_type_compatibility=compatibility,
    )

    healthy_matches = list(getattr(candidate, "healthy_pattern_matches", []) or [])
    if healthy_matches:
        score = max(0.0, score - profile.healthy_suppressor_penalty)
        warnings.append("Healthy reasoning pattern reduced this score.")

    if requires_context and not has_context:
        score = min(score, profile.contextual_isolated_cap)
        if score >= profile.contextual_isolated_cap:
            warnings.append("Contextual/discourse risk capped for an isolated sentence.")

    if len(claim_text) <= profile.short_claim_char_limit and high_confidence_risk_count >= profile.short_claim_high_confidence_limit and confidence >= 0.75:
        score = min(score, 0.49)
        needs_review = True
        warnings.append("Short claim has multiple high-confidence labels; human review recommended.")

    score = round(_bounded(score), 3)
    return ScoredRisk(score, risk_level(score), suppressed=False, needs_human_review=needs_review, warning=" ".join(warnings))


def _taxonomy_match(candidate: Any | None, classification: dict[str, Any]) -> float:
    if candidate is None:
        return 1.0 if classification.get("risk_id") or classification.get("taxonomy_id") else 0.0
    retrieval_score = float(getattr(candidate, "retrieval_score", 0.0) or 0.0)
    return _bounded(0.55 + min(retrieval_score, 4.5) / 10.0)


def _evidence_strength(classification: dict[str, Any], *, exact: bool) -> float:
    span = str(classification.get("evidence_span", "") or "")
    if not span:
        return 0.0
    base = 1.0 if exact else 0.55
    if len(span.strip()) < 4:
        base -= 0.2
    return _bounded(base)


def _consistency_check(entry: Any | None, classification: dict[str, Any], *, has_context: bool) -> float:
    if entry is None:
        return 0.8
    if bool(getattr(entry, "requires_context", False)) and not has_context:
        return 0.45
    if bool(getattr(entry, "requires_human_judgment", False)):
        return 0.75
    return 1.0


def _claim_type_compatibility(entry: Any | None, claim_type: str) -> float:
    category = str(getattr(entry, "canonical_category", "") if entry is not None else "")
    if not claim_type or claim_type == "unclear":
        return 0.7
    if category in {"causal_reasoning_error", "statistical_reasoning_error"}:
        return 1.0 if claim_type in {"causal_claim", "statistical_claim", "evidential_claim"} else 0.65
    if category == "fallacy" and claim_type in {"generalization", "causal_claim", "comparative_claim", "normative_claim"}:
        return 1.0
    return 0.85


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value or 0.0)))
