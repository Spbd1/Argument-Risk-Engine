from __future__ import annotations

from pathlib import Path

from argument_risk_engine.taxonomy.indexer import (
    TaxonomyFilters,
    build_index,
    facet_counts,
    filter_entries,
    search_entries,
)
from argument_risk_engine.taxonomy.loader import load_taxonomy_pack, save_taxonomy_pack
from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack
from argument_risk_engine.taxonomy.quality_audit import coverage_report

from backend.app.core.paths import TAXONOMY_PACK_PATH


def get_active_pack() -> TaxonomyPack:
    return load_taxonomy_pack(TAXONOMY_PACK_PATH)


def save_active_pack(pack: TaxonomyPack) -> None:
    save_taxonomy_pack(pack, TAXONOMY_PACK_PATH)


def list_entries(filters: TaxonomyFilters | None = None) -> list[TaxonomyEntry]:
    entries = get_active_pack().entries
    if filters is None:
        return entries
    return filter_entries(entries, filters)


def get_entry(risk_id: str) -> TaxonomyEntry | None:
    return build_index(get_active_pack()).get(risk_id)


def search_taxonomy(query: str) -> list[TaxonomyEntry]:
    return search_entries(get_active_pack().entries, query)


def categories() -> list[str]:
    return sorted(facet_counts(get_active_pack().entries, "canonical_category"))


def summary() -> dict[str, object]:
    report = coverage_report(get_active_pack())
    return {
        "entry_count": report["entry_count"],
        "active_count": report["active_count"],
        "enabled_for_classification_count": report["enabled_for_classification_count"],
        "by_category": report["by_category"],
        "by_pack": report["by_pack"],
        "by_activation_status": report["by_activation_status"],
    }


def taxonomy_path() -> Path:
    return TAXONOMY_PACK_PATH
