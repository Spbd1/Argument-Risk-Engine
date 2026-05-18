from backend.app.schemas.taxonomy import TaxonomyListResponse
from backend.app.services.taxonomy_service import get_active_pack
from fastapi import APIRouter

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])

@router.get("", response_model=TaxonomyListResponse)
def list_taxonomy() -> TaxonomyListResponse:
    return TaxonomyListResponse(entries=get_active_pack().entries)
