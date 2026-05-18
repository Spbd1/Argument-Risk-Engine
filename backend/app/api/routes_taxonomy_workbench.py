from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from backend.app.schemas.taxonomy_workbench import (
    ActivationRequest,
    ActivationResponse,
    TaxonomyCoverageResponse,
    TaxonomyImportResult,
    TaxonomyPacksResponse,
    TaxonomyQualityResponse,
    TaxonomyValidationResponse,
)
from backend.app.services.taxonomy_workbench_service import (
    coverage,
    export_workbook,
    import_workbook,
    packs,
    quality,
    set_activation,
    validate_current_taxonomy,
)
from fastapi import APIRouter, File, Response, UploadFile

router = APIRouter(prefix="/taxonomy-workbench", tags=["taxonomy-workbench"])


@router.get("/packs", response_model=TaxonomyPacksResponse)
def taxonomy_packs() -> TaxonomyPacksResponse:
    return TaxonomyPacksResponse(**packs())


@router.get("/coverage", response_model=TaxonomyCoverageResponse)
def taxonomy_coverage() -> TaxonomyCoverageResponse:
    return TaxonomyCoverageResponse(**coverage())


@router.get("/quality-report", response_model=TaxonomyQualityResponse)
def taxonomy_quality() -> TaxonomyQualityResponse:
    return TaxonomyQualityResponse(**quality())


@router.post("/validate", response_model=TaxonomyValidationResponse)
def validate_taxonomy() -> TaxonomyValidationResponse:
    return TaxonomyValidationResponse(**validate_current_taxonomy())


@router.post("/import-excel", response_model=TaxonomyImportResult)
def import_taxonomy_excel(file: UploadFile = File(...)) -> TaxonomyImportResult:
    suffix = Path(getattr(file, "filename", "taxonomy.xlsx") or "taxonomy.xlsx").suffix or ".xlsx"
    with NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        content = file.file.read()
        handle.write(content)
        temp_path = Path(handle.name)
    try:
        return TaxonomyImportResult(**import_workbook(temp_path))
    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/export-excel")
def export_taxonomy_excel() -> Response:
    path = export_workbook()
    content = path.read_bytes()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.patch("/entries/{risk_id}/activation", response_model=ActivationResponse)
def update_activation(risk_id: str, request: ActivationRequest) -> ActivationResponse | dict[str, str]:
    try:
        result = set_activation(
            risk_id=risk_id,
            activation_status=request.activation_status,
            enabled_for_classification=request.enabled_for_classification,
        )
    except KeyError:
        return {"detail": "taxonomy entry not found"}
    except ValueError as error:
        return {"detail": str(error)}
    return ActivationResponse(**result)


# Backwards-compatible aliases for the original MVP endpoints.
@router.get("/quality")
def taxonomy_quality_alias() -> TaxonomyQualityResponse:
    return taxonomy_quality()


@router.post("/import")
def import_taxonomy_alias(file: UploadFile = File(...)) -> TaxonomyImportResult:
    return import_taxonomy_excel(file)


@router.get("/export")
def export_taxonomy_alias() -> Response:
    return export_taxonomy_excel()
