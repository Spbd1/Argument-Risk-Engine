from pathlib import Path

from backend.app.services.taxonomy_workbench_service import export_workbook, quality
from fastapi import APIRouter

router = APIRouter(prefix="/taxonomy-workbench", tags=["taxonomy-workbench"])

@router.get("/quality")
def taxonomy_quality() -> dict[str, object]:
    return quality()

@router.get("/export")
def export_taxonomy() -> dict[str, str]:
    path = export_workbook(Path("data/taxonomy/exports/taxonomy.xlsx"))
    return {"path": str(path)}
