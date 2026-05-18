from argument_risk_engine.classification.deterministic import classify_deterministic
from argument_risk_engine.taxonomy.models import default_taxonomy_pack


def test_classifier_returns_match():
    entry = default_taxonomy_pack().entries[0]
    assert classify_deterministic("everyone always", [entry])[0]["taxonomy_id"] == entry.id
