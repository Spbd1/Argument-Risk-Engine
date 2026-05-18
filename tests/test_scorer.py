from argument_risk_engine.scoring.scorer import score_risk


def test_score_risk():
    assert score_risk("high", 0.9) == 0.9
