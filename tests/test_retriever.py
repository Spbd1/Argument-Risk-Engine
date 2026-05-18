from argument_risk_engine.retrieval.lexical_retriever import retrieve_candidates
from argument_risk_engine.taxonomy.models import default_taxonomy_pack


def test_retriever_finds_keyword_candidate():
    matches = retrieve_candidates("Everyone always does this.", default_taxonomy_pack())
    assert matches[0].id == "overgeneralization"
