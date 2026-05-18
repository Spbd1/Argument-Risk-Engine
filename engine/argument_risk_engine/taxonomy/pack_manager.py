from __future__ import annotations

from pathlib import Path

from argument_risk_engine.taxonomy.loader import load_taxonomy_pack
from argument_risk_engine.taxonomy.models import ActivationStatus, CanonicalCategory, TaxonomyEntry, TaxonomyPack, default_taxonomy_pack

ROOT = Path(__file__).resolve().parents[3]
PACKS_DIR = ROOT / "data/taxonomy/packs"


def load_pack(pack_id: str, packs_dir: Path = PACKS_DIR) -> TaxonomyPack:
    return load_taxonomy_pack(packs_dir / f"{pack_id}.yaml")


def load_all_packs(packs_dir: Path = PACKS_DIR) -> TaxonomyPack:
    if not packs_dir.exists():
        return default_taxonomy_pack()
    entries: list[TaxonomyEntry] = []
    for path in sorted(packs_dir.glob("*.yaml")):
        entries.extend(load_taxonomy_pack(path).entries)
    return TaxonomyPack(name="all", entries=entries)


def active_classification_entries(pack: TaxonomyPack | None = None) -> list[TaxonomyEntry]:
    taxonomy = pack or load_all_packs()
    return [
        entry for entry in taxonomy.entries
        if entry.enabled_for_classification
        and entry.activation_status == ActivationStatus.active.value
        and entry.canonical_category != CanonicalCategory.healthy_reasoning_pattern.value
    ]


def active_pack() -> TaxonomyPack:
    entries = active_classification_entries(load_all_packs())
    return TaxonomyPack(name="active", entries=entries)
