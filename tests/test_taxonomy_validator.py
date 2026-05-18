from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack
from argument_risk_engine.taxonomy.validator import validate_taxonomy_pack


def test_validator_detects_duplicate():
    pack = TaxonomyPack(entries=[TaxonomyEntry(id="a", name="A", description="D", keywords=["x"]), TaxonomyEntry(id="a", name="B", description="D", keywords=["y"])])
    assert "duplicate id: a" in validate_taxonomy_pack(pack)
