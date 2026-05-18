from __future__ import annotations

from collections import defaultdict

from argument_risk_engine.taxonomy.models import TaxonomyPack


def build_synonym_map(pack: TaxonomyPack) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for entry in pack.entries:
        for synonym_id in entry.synonym_ids:
            mapping[synonym_id].append(entry.id)
    return dict(mapping)
