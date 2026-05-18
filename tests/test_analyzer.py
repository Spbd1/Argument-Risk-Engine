from argument_risk_engine.analyzer import analyze_text


def test_analyzer_returns_structured_risk_report():
    result = analyze_text("They are vermin.")

    assert result["text_id"].startswith("txt_")
    assert result["mode"] == "deterministic_baseline"
    assert result["llm_used"] is False
    assert result["claims"]
    claim = result["claims"][0]
    assert claim["claim_id"] == "claim_1"
    assert claim["start_char"] == 0
    assert claim["detected_risks"]
    risk = claim["detected_risks"][0]
    assert set(risk) == {
        "risk_id",
        "category",
        "label",
        "severity",
        "confidence",
        "risk_score",
        "risk_level",
        "evidence_span",
        "evidence_start_char",
        "evidence_end_char",
        "explanation",
        "false_positive_warning",
        "needs_human_review",
    }
    assert result["overall_risk_score"] >= risk["risk_score"]


def test_analyzer_response_is_stable_for_same_text():
    first = analyze_text("Everyone always caused this.")
    second = analyze_text("Everyone always caused this.")

    assert first == second


def test_analyzer_can_include_retrieval_diagnostics():
    result = analyze_text("Everyone always caused this.", include_retrieval_diagnostics=True)

    assert isinstance(result["claims"][0]["retrieval_diagnostics"], dict)
    assert "considered_entry_count" in result["claims"][0]["retrieval_diagnostics"]
