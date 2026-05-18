from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_REGISTRY = ROOT / "data/taxonomy/source_registry.yaml"


def load_source_registry(path: Path | str = DEFAULT_SOURCE_REGISTRY) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {"version": "0.2.0", "items": []}
    return yaml.safe_load(file_path.read_text()) or {"version": "0.2.0", "items": []}


def source_ids(path: Path | str = DEFAULT_SOURCE_REGISTRY) -> set[str]:
    data = load_source_registry(path)
    return {str(item.get("source_id")) for item in data.get("items", []) if item.get("source_id")}
