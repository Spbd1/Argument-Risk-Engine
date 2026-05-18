from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from argument_risk_engine.taxonomy.exporter import export_taxonomy_excel
from argument_risk_engine.taxonomy.importer import import_taxonomy_excel
from argument_risk_engine.taxonomy.importer import import_workbook as import_taxonomy_workbook
from argument_risk_engine.taxonomy.loader import load_taxonomy_pack, save_taxonomy_pack
from argument_risk_engine.taxonomy.models import ActivationStatus, TaxonomyEntry, TaxonomyPack
from argument_risk_engine.taxonomy.quality_audit import audit_pack, coverage_report
from argument_risk_engine.taxonomy.validator import validate_taxonomy_pack_detailed

from backend.app.core.paths import DATA_DIR, TAXONOMY_PACK_PATH
from backend.app.services.taxonomy_service import get_active_pack, save_active_pack

PACKS_DIR = DATA_DIR / "taxonomy" / "packs"
BACKUP_DIR = DATA_DIR / "taxonomy" / "backups"
EXPORT_DIR = DATA_DIR / "taxonomy" / "exports"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_file(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{path.stem}.{_timestamp()}{path.suffix}"
    shutil.copy2(path, backup)
    return backup


def backup_pack_files() -> list[Path]:
    backups: list[Path] = []
    for path in sorted(PACKS_DIR.glob("*.yaml")):
        backups.append(backup_file(path))
    return backups


def packs() -> dict[str, object]:
    entries = get_active_pack().entries
    grouped: dict[str, list[TaxonomyEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.pack, []).append(entry)
    return {
        "packs": [
            {
                "pack": pack,
                "entry_count": len(pack_entries),
                "active_count": sum(1 for entry in pack_entries if entry.active),
                "enabled_for_classification_count": sum(1 for entry in pack_entries if entry.enabled_for_classification),
            }
            for pack, pack_entries in sorted(grouped.items())
        ]
    }


def coverage() -> dict[str, Any]:
    return coverage_report(get_active_pack())


def quality() -> dict[str, Any]:
    return audit_pack(get_active_pack())


def validate_current_taxonomy() -> dict[str, Any]:
    report = validate_taxonomy_pack_detailed(get_active_pack())
    return report.to_dict()


def import_workbook(path: Path) -> dict[str, object]:
    if path.suffix.lower() != ".xlsx":
        return {"entry_count": 0, "errors": ["Uploaded taxonomy file must be an .xlsx workbook."], "warnings": [], "backup_paths": []}
    backups = backup_pack_files()
    report = import_taxonomy_workbook(path)
    pack = import_taxonomy_excel(path)
    save_active_pack(pack)
    return {
        "entry_count": len(pack.entries),
        "errors": [issue.message for issue in report.errors],
        "warnings": [issue.message for issue in report.warnings],
        "backup_paths": [str(path) for path in backups],
    }


def export_workbook(path: Path | None = None) -> Path:
    output = path or (EXPORT_DIR / f"taxonomy-{_timestamp()}.xlsx")
    return export_taxonomy_excel(get_active_pack(), output)


def _find_pack_file_for_entry(risk_id: str) -> tuple[Path, TaxonomyPack, TaxonomyEntry] | None:
    candidates = sorted(PACKS_DIR.glob("*.yaml"))
    if TAXONOMY_PACK_PATH not in candidates and TAXONOMY_PACK_PATH.exists():
        candidates.insert(0, TAXONOMY_PACK_PATH)
    for path in candidates:
        pack = load_taxonomy_pack(path)
        for entry in pack.entries:
            if entry.id == risk_id:
                return path, pack, entry
    return None


def set_activation(risk_id: str, activation_status: str, enabled_for_classification: bool | None = None) -> dict[str, object]:
    found = _find_pack_file_for_entry(risk_id)
    if found is None:
        raise KeyError(risk_id)
    path, pack, target = found
    allowed = {item.value for item in ActivationStatus}
    if activation_status not in allowed:
        raise ValueError(f"activation_status must be one of: {', '.join(sorted(allowed))}")
    backup = backup_file(path)
    for index, entry in enumerate(pack.entries):
        if entry.id == risk_id:
            data = entry.model_dump(mode="json")
            data["activation_status"] = activation_status
            if enabled_for_classification is None:
                data["enabled_for_classification"] = activation_status == ActivationStatus.active.value
            else:
                data["enabled_for_classification"] = enabled_for_classification
            pack.entries[index] = TaxonomyEntry(**data)
            target = pack.entries[index]
            break
    save_taxonomy_pack(pack, path)
    if path.resolve() == TAXONOMY_PACK_PATH.resolve():
        save_active_pack(pack)
    return {"entry": target, "backup_path": str(backup)}
