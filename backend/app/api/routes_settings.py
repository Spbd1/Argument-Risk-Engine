from backend.app.schemas.settings import AppSettings
from backend.app.services.settings_service import get_model_settings, update_model_settings
from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=AppSettings)
def get_settings() -> AppSettings:
    return get_model_settings()

@router.put("", response_model=AppSettings)
def put_settings(settings: AppSettings) -> AppSettings:
    return update_model_settings(settings)
