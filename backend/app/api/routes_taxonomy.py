from __future__ import annotations

from argument_risk_engine.taxonomy.indexer import TaxonomyFilters

from backend.app.schemas.taxonomy import (
    TaxonomyCategoriesResponse,
    TaxonomyEntryResponse,
    TaxonomyListResponse,
    TaxonomySearchResponse,
    TaxonomySummaryResponse,
)
from backend.app.services import taxonomy_service
from fastapi import APIRouter


def _bool_filter(value: bool | str | None) -> bool | None:
    if isinstance(value, bool) or value is None:
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "enabled", "active"}:
        return True
    if text in {"false", "0", "no", "disabled", "inactive"}:
        return False
    return None


router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("", response_model=TaxonomyListResponse)
def list_taxonomy(
    category: str | None = None,
    pack: str | None = None,
    academic_status: str | None = None,
    academic_consensus: str | None = None,
    detection_level: str | None = None,
    activation_status: str | None = None,
    enabled_for_classification: bool | None = None,
    false_positive_sensitivity: str | None = None,
) -> TaxonomyListResponse:
    entries = taxonomy_service.list_entries(
        TaxonomyFilters(
            category=category,
            pack=pack,
            academic_status=academic_status,
            academic_consensus=academic_consensus,
            detection_level=detection_level,
            activation_status=activation_status,
            enabled_for_classification=_bool_filter(enabled_for_classification),
            false_positive_sensitivity=false_positive_sensitivity,
        )
    )
    return TaxonomyListResponse(entries=entries, total=len(entries))


@router.get("/search", response_model=TaxonomySearchResponse)
def search_taxonomy(q: str = "") -> TaxonomySearchResponse:
    entries = taxonomy_service.search_taxonomy(q)
    return TaxonomySearchResponse(entries=entries, query=q, total=len(entries))


@router.get("/categories", response_model=TaxonomyCategoriesResponse)
def taxonomy_categories() -> TaxonomyCategoriesResponse:
    return TaxonomyCategoriesResponse(categories=taxonomy_service.categories())


@router.get("/summary", response_model=TaxonomySummaryResponse)
def taxonomy_summary() -> TaxonomySummaryResponse:
    return TaxonomySummaryResponse(**taxonomy_service.summary())


@router.get("/{risk_id}", response_model=TaxonomyEntryResponse)
def get_taxonomy_entry(risk_id: str) -> TaxonomyEntryResponse | dict[str, str]:
    entry = taxonomy_service.get_entry(risk_id)
    if entry is None:
        return {"detail": "taxonomy entry not found"}
    return TaxonomyEntryResponse(entry=entry)
