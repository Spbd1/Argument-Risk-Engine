from pathlib import Path
from tempfile import NamedTemporaryFile

from backend.app.services.taxonomy_workbench_service import export_workbook, import_workbook, quality
from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/taxonomy-workbench", tags=["taxonomy-workbench"])


@router.get("/quality")
def taxonomy_quality() -> dict[str, object]:
    return quality()


@router.post("/import")
def import_taxonomy(file: UploadFile = File(...)) -> dict[str, object]:
    suffix = Path(getattr(file, "filename", "taxonomy.xlsx") or "taxonomy.xlsx").suffix or ".xlsx"
    with NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        content = file.file.read()
        handle.write(content)
        temp_path = Path(handle.name)
    try:
        return import_workbook(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/export")
def export_taxonomy() -> dict[str, str]:
    path = export_workbook(Path("data/taxonomy/exports/taxonomy.xlsx"))
    return {"path": str(path)}
