from __future__ import annotations

from argument_risk_engine.retrieval.inverted_index import tokenize
from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack


def retrieve_candidates(claim: str, pack: TaxonomyPack, limit: int = 5) -> list[TaxonomyEntry]:
    claim_text = claim.lower()
    claim_tokens = set(tokenize(claim))
    scored: list[tuple[int, TaxonomyEntry]] = []
    for entry in pack.entries:
        if not entry.active:
            continue
        score = 0
        for keyword in entry.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in claim_text:
                score += 3
            score += len(set(tokenize(keyword_lower)) & claim_tokens)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: (-item[0], item[1].id))
    return [entry for _, entry in scored[:limit]]
