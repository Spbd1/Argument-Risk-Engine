from argument_risk_engine.extraction.claim_extractor import extract_claims


def test_extract_claims_splits_sentences():
    assert len(extract_claims("First claim. Second claim.")) == 2
