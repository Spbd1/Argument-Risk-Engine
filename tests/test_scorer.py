from argument_risk_engine.scoring.calibration import risk_level
from argument_risk_engine.scoring.scorer import (
    calculate_risk_score,
    score_classification,
    score_risk,
)


def test_weighted_formula_matches_spec():
    assert calculate_risk_score(
        taxonomy_match=1.0,
        evidence_strength=0.8,
        classifier_confidence=0.9,
        severity_weight_value=1.0,
        consistency_check=0.5,
        claim_type_compatibility=1.0,
    ) == 0.88


def test_legacy_score_risk_still_available():
    assert score_risk("high", 0.9) == 0.9


def test_false_positive_guards_suppress_missing_evidence_and_low_confidence():
    missing = score_classification({"severity": "high", "confidence": 0.9, "evidence_span": ""})
    low_confidence = score_classification({"severity": "high", "confidence": 0.44, "evidence_span": "always"})

    assert missing.suppressed is True
    assert low_confidence.suppressed is True


def test_risk_level_thresholds_are_stable():
    assert risk_level(0.0) == "low"
    assert risk_level(0.25) == "moderate"
    assert risk_level(0.5) == "high"
    assert risk_level(0.75) == "severe"
