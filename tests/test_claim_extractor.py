from argument_risk_engine.explanation.evidence import find_evidence_spans
from argument_risk_engine.extraction.claim_extractor import extract_claims


def test_extract_claims_splits_sentences():
    assert len(extract_claims("First claim. Second claim.")) == 2


def test_extract_claims_preserves_offsets_and_types():
    text = "Intro. Prices will likely rise because supply is low. Should we wait?"
    claims = extract_claims(text)

    assert [claim.text for claim in claims] == [
        "Prices will likely rise because supply is low.",
        "Should we wait?",
    ]
    assert claims[0].claim_type == "causal_claim"
    assert claims[1].claim_type == "question_claim"
    for claim in claims:
        assert text[claim.start_char : claim.end_char] == claim.text


def test_extract_claims_ignores_short_fragments_without_markers():
    claims = extract_claims("Wow. Too vague. This report should be reviewed.")

    assert [claim.text for claim in claims] == ["This report should be reviewed."]
    assert claims[0].claim_type == "normative_claim"


def test_evidence_spans_are_exact_substrings_only():
    text = "The survey found that 62 percent agreed."

    spans = find_evidence_spans(text, "survey found")
    assert len(spans) == 1
    assert spans[0].text == "survey found"
    assert text[spans[0].start_char : spans[0].end_char] == spans[0].text
    assert find_evidence_spans(text, "survey invented") == []
