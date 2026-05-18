from __future__ import annotations

from argument_risk_engine.classification.model_provider import ProviderProfile

from backend.app.schemas.settings import (
    ActiveProviderRequest,
    ActiveProviderResponse,
    AppSettings,
    ProviderListResponse,
    ProviderProfilePatch,
    ProviderProfileSchema,
    ProviderTestResponse,
)
from backend.app.services.settings_service import (
    get_active_model_provider,
    get_model_settings,
    list_model_providers,
    patch_model_provider,
    save_model_provider,
    set_active_model_provider,
    test_model_provider,
    update_model_settings,
)
from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=AppSettings)
def get_settings() -> AppSettings:
    return get_model_settings()


@router.put("", response_model=AppSettings)
def put_settings(settings: AppSettings) -> AppSettings:
    return update_model_settings(settings)


@router.get("/model-providers", response_model=ProviderListResponse)
def get_model_providers() -> ProviderListResponse:
    return ProviderListResponse(providers=[ProviderProfileSchema(**profile.model_dump()) for profile in list_model_providers()])


@router.post("/model-providers", response_model=ProviderProfileSchema)
def post_model_provider(profile: ProviderProfileSchema) -> ProviderProfileSchema:
    saved = save_model_provider(ProviderProfile(**profile.model_dump()))
    return ProviderProfileSchema(**saved.model_dump())


@router.patch("/model-providers/{provider_id}", response_model=ProviderProfileSchema)
def patch_model_provider_route(provider_id: str, patch: ProviderProfilePatch) -> ProviderProfileSchema | dict[str, str]:
    updated = patch_model_provider(provider_id, patch.model_dump())
    if updated is None:
        return {"detail": "provider not found"}
    return ProviderProfileSchema(**updated.model_dump())


@router.post("/model-providers/{provider_id}/test", response_model=ProviderTestResponse)
def test_model_provider_route(provider_id: str) -> ProviderTestResponse | dict[str, str]:
    result = test_model_provider(provider_id)
    if result is None:
        return {"detail": "provider not found"}
    return ProviderTestResponse(**result.model_dump())


@router.get("/active-model-provider", response_model=ActiveProviderResponse)
def get_active_model_provider_route() -> ActiveProviderResponse:
    provider_id, provider = get_active_model_provider()
    return ActiveProviderResponse(provider_id=provider_id, provider=ProviderProfileSchema(**provider.model_dump()) if provider else None)


@router.post("/active-model-provider", response_model=ActiveProviderResponse)
def post_active_model_provider(payload: ActiveProviderRequest) -> ActiveProviderResponse | dict[str, str]:
    provider_id, provider = set_active_model_provider(payload.provider_id)
    if provider is None:
        return {"detail": "provider not found"}
    return ActiveProviderResponse(provider_id=provider_id, provider=ProviderProfileSchema(**provider.model_dump()))
