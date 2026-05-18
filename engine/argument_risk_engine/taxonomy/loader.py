from __future__ import annotations

from pathlib import Path

import yaml
from argument_risk_engine.taxonomy.models import (
    RiskSeverity,
    TaxonomyEntry,
    TaxonomyPack,
    default_taxonomy_pack,
)


def load_taxonomy_pack(path: Path | str | None = None) -> TaxonomyPack:
    if path is None:
        return default_taxonomy_pack()
    file_path = Path(path)
    if not file_path.exists():
        return default_taxonomy_pack()
    data = yaml.safe_load(file_path.read_text())
    if not data:
        return default_taxonomy_pack()
    entries = []
    for entry in data.get("entries", []):
        if isinstance(entry, TaxonomyEntry):
            entries.append(entry)
        else:
            item = dict(entry)
            item["severity"] = RiskSeverity(str(item.get("severity", "low")))
            entries.append(TaxonomyEntry(**item))
    return TaxonomyPack(
        version=str(data.get("version", "0.1.0")),
        name=str(data.get("name", "default")),
        entries=entries,
    )


def save_taxonomy_pack(pack: TaxonomyPack, path: Path | str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(yaml.safe_dump(pack.model_dump(mode="json"), sort_keys=False))
