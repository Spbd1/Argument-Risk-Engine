from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyEntry


def is_deprecated(entry: TaxonomyEntry) -> bool:
    return entry.activation_status == "deprecated" or entry.academic_status == "deprecated"


def is_healthy_suppressor(entry: TaxonomyEntry) -> bool:
    return bool(entry.healthy_suppressor or entry.canonical_category == "healthy_reasoning_pattern")


def is_candidate_only(entry: TaxonomyEntry) -> bool:
    return bool(entry.enabled_for_retrieval and not entry.enabled_for_classification)


def final_classification_candidates(candidates: list[object]) -> list[object]:
    """Drop deprecated, healthy-suppressor, and candidate-only retrieval matches."""

    filtered: list[object] = []
    for candidate in candidates:
        entry = getattr(candidate, "entry", candidate)
        if is_deprecated(entry) or is_healthy_suppressor(entry) or is_candidate_only(entry):
            continue
        filtered.append(candidate)
    return filtered
