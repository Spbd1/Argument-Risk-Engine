from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyEntry


def classify_deterministic(claim: str, candidates: list[TaxonomyEntry]) -> list[dict[str, object]]:
    lower = claim.lower()
    results: list[dict[str, object]] = []
    for entry in candidates:
        matched = [kw for kw in entry.keywords if kw.lower() in lower]
        if matched:
            confidence = min(0.95, 0.45 + 0.15 * len(matched))
            results.append({"taxonomy_id": entry.id, "confidence": confidence, "matched_terms": matched})
    return results
