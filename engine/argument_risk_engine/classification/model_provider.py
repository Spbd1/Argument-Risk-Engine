from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ProviderType = Literal["deterministic", "openai_compatible"]


class ProviderProfile(BaseModel):
    provider_id: str
    label: str
    provider_type: ProviderType = "openai_compatible"
    base_url: str = ""
    model_name: str = ""
    api_key_env_var: str = ""
    timeout_seconds: int = 60
    max_tokens: int = 2048
    temperature: float = 0.0
    supports_json_mode: str | bool = "unknown"
    supports_streaming: str | bool = "unknown"
    enabled: bool = False

    def sanitized(self) -> ProviderProfile:
        """Return a copy containing only metadata, never an API key value."""
        return ProviderProfile(**self.model_dump())

    @property
    def requires_secret(self) -> bool:
        return self.provider_type == "openai_compatible" and bool(self.api_key_env_var)

    @property
    def is_remote(self) -> bool:
        return self.base_url.startswith("https://") and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url


class ModelProvider(BaseModel):
    name: str = "deterministic_baseline"
    model: str = "local-keyword"
    temperature: float = 0.0
