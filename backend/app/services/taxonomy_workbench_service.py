from pathlib import Path

from argument_risk_engine.taxonomy.exporter import export_taxonomy_excel
from argument_risk_engine.taxonomy.importer import import_taxonomy_excel
from argument_risk_engine.taxonomy.validator import validate_taxonomy_pack

from backend.app.services.taxonomy_service import get_active_pack, save_active_pack


def quality() -> dict[str, object]:
    pack = get_active_pack()
    return {"errors": validate_taxonomy_pack(pack), "entry_count": len(pack.entries)}


def import_workbook(path: Path) -> dict[str, object]:
    pack = import_taxonomy_excel(path)
    save_active_pack(pack)
    return {"entry_count": len(pack.entries)}


def export_workbook(path: Path) -> Path:
    return export_taxonomy_excel(get_active_pack(), path)
