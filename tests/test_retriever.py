from argument_risk_engine.retrieval.candidate_filter import final_classification_candidates
from argument_risk_engine.retrieval.lexical_retriever import retrieve_candidates
from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack, default_taxonomy_pack


def _entry(**overrides):
    data = {
        "id": "risk",
        "name": "Risk",
        "signals": ["always"],
        "enabled_for_retrieval": True,
        "enabled_for_classification": True,
        "activation_status": "active",
    }
    data.update(overrides)
    return TaxonomyEntry(**data)


def test_retriever_finds_keyword_candidate():
    matches = retrieve_candidates("Everyone always does this.", default_taxonomy_pack())
    assert matches[0].id == "overgeneralization"


def test_retriever_ignores_deprecated_and_limits_neutral_text():
    pack = TaxonomyPack(
        entries=[
            _entry(id=f"neutral_{idx}", name=f"Neutral {idx}", signals=[f"rareterm{idx}"])
            for idx in range(1000)
        ]
        + [_entry(id="deprecated", name="Deprecated", signals=["uniquehit"], activation_status="deprecated")]
    )

    assert retrieve_candidates("This is a neutral project update with ordinary wording.", pack, limit=20) == []
    assert retrieve_candidates("uniquehit appears here.", pack) == []


def test_candidate_only_entries_are_retrieved_but_not_final_candidates():
    pack = TaxonomyPack(
        entries=[
            _entry(id="candidate_only", name="Candidate only", signals=["specialmarker"], enabled_for_classification=False),
            _entry(id="final", name="Final", signals=["specialmarker"]),
        ]
    )

    matches = retrieve_candidates("The text uses specialmarker.", pack, limit=10)
    ids = {match.id for match in matches}
    assert {"candidate_only", "final"} <= ids
    assert [match.id for match in final_classification_candidates(matches)] == ["final"]


def test_healthy_reasoning_patterns_reduce_risky_matches():
    risky = _entry(id="overgeneralization", name="Overgeneralization", signals=["always"])
    healthy = _entry(
        id="qualified_reasoning",
        name="Qualified reasoning",
        canonical_category="healthy_reasoning_pattern",
        signals=["usually", "always"],
        healthy_suppressor=True,
    )
    pack_without_suppressor = TaxonomyPack(entries=[risky])
    pack_with_suppressor = TaxonomyPack(entries=[risky, healthy])

    baseline = retrieve_candidates("People always do this.", pack_without_suppressor)[0]
    reduced = retrieve_candidates("People usually always do this.", pack_with_suppressor)[0]

    assert reduced.id == "overgeneralization"
    assert reduced.retrieval_score < baseline.retrieval_score
    assert reduced.healthy_pattern_matches == ["qualified_reasoning"]
    assert reduced.diagnostics["healthy_suppressor_count"] == 1
