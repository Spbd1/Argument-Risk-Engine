from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack
from argument_risk_engine.taxonomy.validator import (
    validate_taxonomy_pack,
    validate_taxonomy_pack_detailed,
)


def test_validator_detects_duplicate():
    pack = TaxonomyPack(entries=[TaxonomyEntry(id="a", name="A", description="D", keywords=["x"]), TaxonomyEntry(id="a", name="B", description="D", keywords=["y"])])
    assert "duplicate id: a" in validate_taxonomy_pack(pack)


def test_validator_reports_active_classification_requirements_with_row_number():
    pack = TaxonomyPack(entries=[TaxonomyEntry(id="Thin Evidence", name="Thin", enabled_for_classification=True, activation_status="active", row_number=42)])
    report = validate_taxonomy_pack_detailed(pack)
    assert not report.ok
    issue = report.errors[0]
    assert issue.row_number == 42
    assert issue.entry_id == "thin_evidence"


def test_validator_blocks_healthy_reasoning_classification():
    pack = TaxonomyPack(entries=[TaxonomyEntry(id="healthy", name="Healthy", canonical_category="healthy_reasoning_pattern", enabled_for_classification=True, activation_status="active")])
    messages = validate_taxonomy_pack(pack)
    assert any("must not be returned as a risk" in message for message in messages)
