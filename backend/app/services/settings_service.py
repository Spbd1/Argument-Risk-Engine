from __future__ import annotations

from pathlib import Path
from typing import Any

from argument_risk_engine.classification.llm_client import LLMClient, ProviderTestResult
from argument_risk_engine.classification.model_provider import ProviderProfile
from argument_risk_engine.classification.provider_registry import ProviderRegistry

import yaml
from backend.app.core.paths import DATA_DIR
from backend.app.schemas.settings import AppSettings

MODEL_PROFILES_PATH = DATA_DIR / "config" / "model_profiles.yaml"
APP_SETTINGS_PATH = DATA_DIR / "config" / "app_settings.yaml"

_registry = ProviderRegistry(MODEL_PROFILES_PATH)


def get_model_settings() -> AppSettings:
    payload = _read_yaml(APP_SETTINGS_PATH)
    provider_id = payload.get("active_model_provider") or payload.get("llm_provider") or "deterministic_baseline"
    return AppSettings(
        llm_provider=payload.get("llm_provider", provider_id),
        model=payload.get("model", "local-keyword"),
        temperature=float(payload.get("temperature", 0.0)),
        active_model_provider=provider_id,
    )


def update_model_settings(settings: AppSettings) -> AppSettings:
    provider_id = settings.llm_provider or settings.active_model_provider
    payload = settings.model_dump()
    payload["active_model_provider"] = settings.active_model_provider or provider_id
    payload["llm_provider"] = provider_id
    _write_yaml(APP_SETTINGS_PATH, payload)
    return get_model_settings()


def list_model_providers() -> list[ProviderProfile]:
    return [_sanitize(profile) for profile in _registry.list_profiles()]


def save_model_provider(profile: ProviderProfile) -> ProviderProfile:
    return _sanitize(_registry.upsert_profile(profile))


def patch_model_provider(provider_id: str, patch: dict[str, Any]) -> ProviderProfile | None:
    patch.pop("api_key", None)
    patch.pop("raw_api_key", None)
    updated = _registry.patch_profile(provider_id, patch)
    return _sanitize(updated) if updated else None


def get_active_model_provider() -> tuple[str, ProviderProfile | None]:
    settings = get_model_settings()
    profile = _registry.get_profile(settings.active_model_provider)
    return settings.active_model_provider, _sanitize(profile) if profile else None


def set_active_model_provider(provider_id: str) -> tuple[str, ProviderProfile | None]:
    profile = _registry.get_profile(provider_id)
    if profile is None:
        return provider_id, None
    settings = get_model_settings()
    settings.active_model_provider = provider_id
    settings.llm_provider = provider_id
    settings.model = profile.model_name or settings.model
    settings.temperature = float(profile.temperature)
    update_model_settings(settings)
    return provider_id, _sanitize(profile)


def test_model_provider(provider_id: str) -> ProviderTestResult | None:
    profile = _registry.get_profile(provider_id)
    if profile is None:
        return None
    return LLMClient(profile).test_provider()


def _sanitize(profile: ProviderProfile | None) -> ProviderProfile | None:
    if profile is None:
        return None
    return ProviderProfile(**profile.model_dump())


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
