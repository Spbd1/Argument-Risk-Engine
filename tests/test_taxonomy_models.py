from argument_risk_engine.taxonomy.models import TaxonomyEntry, default_taxonomy_pack


def test_default_pack_has_entries():
    pack = default_taxonomy_pack()
    assert pack.entries
    assert TaxonomyEntry(id="x", name="X", description="Desc").id == "x"
