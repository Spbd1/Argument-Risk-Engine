from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyEntry


def explain(entry: TaxonomyEntry, matched_terms: list[str]) -> str:
    terms = ", ".join(matched_terms) if matched_terms else "taxonomy language"
    return f"Matched {entry.name} because the claim contains {terms}. This is a review signal, not a truth judgement."
