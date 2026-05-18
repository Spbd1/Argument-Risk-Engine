from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack, normalize_id


@dataclass(frozen=True)
class TaxonomyFilters:
    category: str | None = None
    pack: str | None = None
    academic_status: str | None = None
    academic_consensus: str | None = None
    detection_level: str | None = None
    activation_status: str | None = None
    enabled_for_classification: bool | None = None
    false_positive_sensitivity: str | None = None


def build_index(pack: TaxonomyPack) -> dict[str, TaxonomyEntry]:
    """Build an id -> entry lookup for a taxonomy pack."""
    return {entry.id: entry for entry in pack.entries}


def searchable_text(entry: TaxonomyEntry) -> str:
    parts: list[str] = [
        entry.id,
        entry.name,
        entry.pack,
        entry.canonical_category,
        entry.academic_status,
        entry.academic_consensus,
        entry.short_definition,
        entry.long_definition,
        entry.detection_level,
        entry.minimum_evidence_requirement,
        entry.notes,
    ]
    for value in [
        entry.signals,
        entry.trigger_patterns,
        entry.exclusion_criteria,
        entry.common_false_positives,
        entry.positive_examples,
        entry.negative_examples,
        entry.severity_guidance,
        entry.related_risks,
        entry.synonym_ids,
        entry.source_refs,
    ]:
        parts.extend(value)
    return " ".join(str(part) for part in parts if part).lower()


def _matches(value: str, expected: str | None) -> bool:
    if expected in (None, "", "all"):
        return True
    return normalize_id(value) == normalize_id(expected)


def filter_entries(entries: Iterable[TaxonomyEntry], filters: TaxonomyFilters) -> list[TaxonomyEntry]:
    filtered: list[TaxonomyEntry] = []
    for entry in entries:
        if not _matches(entry.canonical_category, filters.category):
            continue
        if not _matches(entry.pack, filters.pack):
            continue
        if not _matches(entry.academic_status, filters.academic_status):
            continue
        if not _matches(entry.academic_consensus, filters.academic_consensus):
            continue
        if not _matches(entry.detection_level, filters.detection_level):
            continue
        if not _matches(entry.activation_status, filters.activation_status):
            continue
        if not _matches(entry.false_positive_sensitivity, filters.false_positive_sensitivity):
            continue
        if filters.enabled_for_classification is not None and entry.enabled_for_classification != filters.enabled_for_classification:
            continue
        filtered.append(entry)
    return filtered


def search_entries(entries: Iterable[TaxonomyEntry], query: str | None) -> list[TaxonomyEntry]:
    if not query:
        return list(entries)
    terms = [term for term in normalize_id(query).split("_") if term]
    if not terms:
        return list(entries)
    scored: list[tuple[int, TaxonomyEntry]] = []
    for entry in entries:
        text = searchable_text(entry)
        if all(term in text for term in terms):
            score = sum(text.count(term) for term in terms)
            if any(term in entry.id.lower() for term in terms):
                score += 5
            if any(term in entry.name.lower() for term in terms):
                score += 3
            scored.append((score, entry))
    return [entry for _, entry in sorted(scored, key=lambda item: (-item[0], item[1].id))]


def facet_counts(entries: Iterable[TaxonomyEntry], field_name: str) -> dict[str, int]:
    counts = Counter(str(getattr(entry, field_name, "") or "unknown") for entry in entries)
    return dict(sorted(counts.items()))
