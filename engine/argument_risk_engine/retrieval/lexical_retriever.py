from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from argument_risk_engine.retrieval.inverted_index import (
    FIELD_WEIGHTS,
    InvertedIndex,
    normalize_phrase,
    significant_terms,
)
from argument_risk_engine.retrieval.retrieval_diagnostics import RetrievalDiagnostics
from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack


@dataclass(frozen=True)
class RetrievedTaxonomyEntry:
    entry: TaxonomyEntry
    retrieval_score: float
    matched_terms: list[str]
    matched_fields: list[str]
    retrieval_reason: str
    false_positive_risk: str = "medium"
    healthy_pattern_matches: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.entry, name)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["entry"] = self.entry.model_dump() if hasattr(self.entry, "model_dump") else self.entry.dict()
        return data


def retrieve_candidates(claim: str, pack: TaxonomyPack, limit: int = 5) -> list[RetrievedTaxonomyEntry]:
    """Retrieve deterministic taxonomy candidates for a claim.

    Retrieval is lexical and conservative: stopwords/generic taxonomy wording do not
    activate entries, deprecated rows are ignored, and matched healthy-reasoning
    patterns lower the scores of risky candidates.
    """

    index = _build_index(pack)
    query = str(claim)
    query_terms = significant_terms(query)
    query_term_set = set(query_terms)
    query_phrase = normalize_phrase(query)

    raw_ids = index.search(query)
    raw_candidates: list[RetrievedTaxonomyEntry] = []
    healthy_matches: list[str] = []
    healthy_terms: set[str] = set()

    for doc_id in sorted(raw_ids):
        indexed = index.get(doc_id)
        if indexed is None:
            continue
        score, matched_terms, matched_fields = _score_indexed_entry(indexed, query_phrase, query_term_set)
        if score <= 0:
            continue
        if indexed.is_healthy_suppressor:
            healthy_matches.append(indexed.entry.id)
            healthy_terms.update(matched_terms)
            continue
        raw_candidates.append(
            RetrievedTaxonomyEntry(
                entry=indexed.entry,
                retrieval_score=score,
                matched_terms=matched_terms,
                matched_fields=matched_fields,
                retrieval_reason=_reason(matched_terms, matched_fields),
                false_positive_risk=_base_false_positive_risk(indexed.entry),
                diagnostics={},
            )
        )

    adjusted: list[RetrievedTaxonomyEntry] = []
    suppressed_count = 0
    for candidate in raw_candidates:
        overlap = sorted(set(candidate.matched_terms) & healthy_terms)
        penalty = 0.0
        if healthy_matches:
            penalty += 1.0
        if overlap:
            penalty += 1.5
        score = max(0.0, candidate.retrieval_score - penalty)
        if score <= 0:
            suppressed_count += 1
            continue
        risk = candidate.false_positive_risk
        if penalty >= 1.5:
            risk = "high"
        elif penalty > 0 and risk == "low":
            risk = "medium"
        adjusted.append(
            RetrievedTaxonomyEntry(
                entry=candidate.entry,
                retrieval_score=round(score, 4),
                matched_terms=candidate.matched_terms,
                matched_fields=candidate.matched_fields,
                retrieval_reason=(candidate.retrieval_reason + "; reduced by healthy reasoning pattern" if penalty else candidate.retrieval_reason),
                false_positive_risk=risk,
                healthy_pattern_matches=healthy_matches,
                diagnostics={},
            )
        )

    adjusted.sort(key=lambda item: (-item.retrieval_score, item.entry.id))
    returned = adjusted[: max(limit, 0)]
    diag = RetrievalDiagnostics(
        query_terms=query_terms,
        considered_entry_count=len(index.entries),
        raw_candidate_count=len(raw_candidates),
        returned_candidate_count=len(returned),
        suppressed_candidate_count=suppressed_count,
        healthy_suppressor_count=len(healthy_matches),
        ignored_terms=sorted(set(normalize_phrase(query).split()) - set(query_terms)),
    ).to_dict()

    return [
        RetrievedTaxonomyEntry(
            entry=item.entry,
            retrieval_score=item.retrieval_score,
            matched_terms=item.matched_terms,
            matched_fields=item.matched_fields,
            retrieval_reason=item.retrieval_reason,
            false_positive_risk=item.false_positive_risk,
            healthy_pattern_matches=item.healthy_pattern_matches,
            diagnostics=diag,
        )
        for item in returned
    ]


def _score_indexed_entry(indexed: Any, query_phrase: str, query_terms: set[str]) -> tuple[float, list[str], list[str]]:
    score = 0.0
    matched_terms: set[str] = set()
    matched_fields: set[str] = set()

    for indexed_field in indexed.fields:
        field_weight = FIELD_WEIGHTS.get(indexed_field.field, 1.0)
        field_terms = set(indexed_field.terms)
        term_hits = field_terms & query_terms
        if term_hits:
            matched_terms.update(term_hits)
            matched_fields.add(indexed_field.field)
            score += field_weight * len(term_hits)
        if indexed_field.phrase and " " in indexed_field.phrase and _phrase_in_query(indexed_field.phrase, query_phrase):
            matched_fields.add(indexed_field.field)
            matched_terms.update(indexed_field.terms)
            score += field_weight * 2.5
        elif indexed_field.phrase and indexed_field.phrase in query_terms:
            matched_fields.add(indexed_field.field)
            matched_terms.update(indexed_field.terms)
            score += field_weight

    # Require either a phrase match, a trigger/signal match, or two meaningful
    # definition/name overlaps. This keeps neutral prose from retrieving many rows.
    strong_field = bool({"signals", "trigger_patterns", "synonyms"} & matched_fields)
    if not strong_field and len(matched_terms) < 2:
        return 0.0, [], []

    if indexed.is_candidate_only:
        score *= 0.9

    return score, sorted(matched_terms), sorted(matched_fields)


def _phrase_in_query(phrase: str, query_phrase: str) -> bool:
    return f" {phrase} " in f" {query_phrase} "


def _reason(matched_terms: list[str], matched_fields: list[str]) -> str:
    fields = ", ".join(matched_fields) if matched_fields else "taxonomy fields"
    terms = ", ".join(matched_terms[:6]) if matched_terms else "phrase"
    return f"Matched {terms} in {fields}."


def _base_false_positive_risk(entry: TaxonomyEntry) -> str:
    sensitivity = str(entry.false_positive_sensitivity or "medium")
    if entry.requires_context or entry.requires_human_judgment or sensitivity == "high":
        return "high"
    if sensitivity == "low":
        return "low"
    return "medium"


def _pack_cache_key(pack: TaxonomyPack) -> tuple[Any, ...]:
    return (
        pack.name,
        pack.version,
        len(pack.entries),
        tuple((entry.id, entry.activation_status, entry.enabled_for_retrieval, entry.enabled_for_classification) for entry in pack.entries),
    )


_INDEX_CACHE: dict[tuple[Any, ...], InvertedIndex] = {}


def _build_index(pack: TaxonomyPack) -> InvertedIndex:
    key = _pack_cache_key(pack)
    cached = _INDEX_CACHE.get(key)
    if cached is not None:
        return cached
    index = InvertedIndex(pack)
    if len(_INDEX_CACHE) > 16:
        _INDEX_CACHE.clear()
    _INDEX_CACHE[key] = index
    return index
