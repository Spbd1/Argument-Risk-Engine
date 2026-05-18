from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from argument_risk_engine.classification.model_provider import ProviderProfile

DEFAULT_PROFILES: list[dict[str, Any]] = [
    {
        "provider_id": "deterministic_baseline",
        "label": "Deterministic Baseline",
        "provider_type": "deterministic",
        "base_url": "",
        "model_name": "local-keyword",
        "api_key_env_var": "",
        "timeout_seconds": 30,
        "max_tokens": 0,
        "temperature": 0.0,
        "supports_json_mode": True,
        "supports_streaming": False,
        "enabled": True,
    },
    {
        "provider_id": "lm_studio_local",
        "label": "LM Studio Local",
        "provider_type": "openai_compatible",
        "base_url": "http://localhost:1234/v1",
        "model_name": "local-model",
        "api_key_env_var": "LM_STUDIO_API_KEY",
        "timeout_seconds": 60,
        "max_tokens": 2048,
        "temperature": 0.0,
        "supports_json_mode": "unknown",
        "supports_streaming": True,
        "enabled": True,
    },
    {
        "provider_id": "ollama_local",
        "label": "Ollama Local",
        "provider_type": "openai_compatible",
        "base_url": "http://localhost:11434/v1",
        "model_name": "qwen3:8b",
        "api_key_env_var": "OLLAMA_API_KEY",
        "timeout_seconds": 60,
        "max_tokens": 2048,
        "temperature": 0.0,
        "supports_json_mode": "unknown",
        "supports_streaming": True,
        "enabled": True,
    },
    {
        "provider_id": "openai_remote",
        "label": "OpenAI Remote",
        "provider_type": "openai_compatible",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4.1-mini",
        "api_key_env_var": "OPENAI_API_KEY",
        "timeout_seconds": 60,
        "max_tokens": 2048,
        "temperature": 0.0,
        "supports_json_mode": True,
        "supports_streaming": True,
        "enabled": True,
    },
    {
        "provider_id": "openrouter_remote",
        "label": "OpenRouter Remote",
        "provider_type": "openai_compatible",
        "base_url": "https://openrouter.ai/api/v1",
        "model_name": "",
        "api_key_env_var": "OPENROUTER_API_KEY",
        "timeout_seconds": 60,
        "max_tokens": 2048,
        "temperature": 0.0,
        "supports_json_mode": "model_dependent",
        "supports_streaming": True,
        "enabled": True,
    },
    {
        "provider_id": "custom_openai_compatible",
        "label": "Custom OpenAI-Compatible",
        "provider_type": "openai_compatible",
        "base_url": "",
        "model_name": "",
        "api_key_env_var": "CUSTOM_LLM_API_KEY",
        "timeout_seconds": 60,
        "max_tokens": 2048,
        "temperature": 0.0,
        "supports_json_mode": "unknown",
        "supports_streaming": "unknown",
        "enabled": False,
    },
]


class ProviderRegistry:
    def __init__(self, path: Path):
        self.path = path

    def list_profiles(self) -> list[ProviderProfile]:
        payload = self._read_payload()
        items = payload.get("items", DEFAULT_PROFILES)
        return [self._profile_from_item(item) for item in items]

    def get_profile(self, provider_id: str) -> ProviderProfile | None:
        return next((profile for profile in self.list_profiles() if profile.provider_id == provider_id), None)

    def upsert_profile(self, profile: ProviderProfile) -> ProviderProfile:
        profiles = self.list_profiles()
        updated = False
        for index, existing in enumerate(profiles):
            if existing.provider_id == profile.provider_id:
                profiles[index] = profile
                updated = True
                break
        if not updated:
            profiles.append(profile)
        self.save_profiles(profiles)
        return profile

    def patch_profile(self, provider_id: str, patch: dict[str, Any]) -> ProviderProfile | None:
        profile = self.get_profile(provider_id)
        if profile is None:
            return None
        data = profile.model_dump()
        data.update({key: value for key, value in patch.items() if value is not None})
        updated = ProviderProfile(**data)
        return self.upsert_profile(updated)

    def save_profiles(self, profiles: list[ProviderProfile]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": "1.0", "items": [profile.model_dump() for profile in profiles]}
        self.path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    def _read_payload(self) -> dict[str, Any]:
        if not self.path.exists():
            self.save_profiles([ProviderProfile(**item) for item in DEFAULT_PROFILES])
        payload = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not payload.get("items"):
            payload["items"] = DEFAULT_PROFILES
        return payload

    @staticmethod
    def _profile_from_item(item: dict[str, Any]) -> ProviderProfile:
        normalized = dict(item)
        if "model_name" not in normalized and "default_model" in normalized:
            normalized["model_name"] = normalized.pop("default_model")
        if "enabled" not in normalized and "enabled_default" in normalized:
            normalized["enabled"] = str(normalized.pop("enabled_default")).lower() in {"yes", "true", "1"}
        for int_field in ("timeout_seconds", "max_tokens"):
            if int_field in normalized:
                normalized[int_field] = int(normalized[int_field] or 0)
        if "temperature" in normalized:
            normalized["temperature"] = float(normalized["temperature"] or 0)
        normalized.pop("security_note", None)
        return ProviderProfile(**normalized)


PROVIDERS = {item["provider_id"]: item["label"] for item in DEFAULT_PROFILES}
