from argument_risk_engine.analyzer import analyze_text


def test_analyzer_returns_risks():
    result = analyze_text("They are vermin.")
    assert result["summary"]["risk_count"] == 1
    assert result["summary"]["highest_severity"] == "high"
