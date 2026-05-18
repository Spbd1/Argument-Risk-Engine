from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyPack


def validate_taxonomy_pack(pack: TaxonomyPack) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for entry in pack.entries:
        if entry.id in seen:
            errors.append(f"duplicate id: {entry.id}")
        seen.add(entry.id)
        if not entry.keywords:
            errors.append(f"{entry.id} has no keywords")
    return errors
