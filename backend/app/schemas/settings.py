from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ProviderType = Literal["deterministic", "openai_compatible"]


class ProviderProfileSchema(BaseModel):
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
    enabled: bool = True


class ProviderProfilePatch(BaseModel):
    label: str | None = None
    provider_type: ProviderType | None = None
    base_url: str | None = None
    model_name: str | None = None
    api_key_env_var: str | None = None
    timeout_seconds: int | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    supports_json_mode: str | bool | None = None
    supports_streaming: str | bool | None = None
    enabled: bool | None = None


class ProviderListResponse(BaseModel):
    providers: list[ProviderProfileSchema] = Field(default_factory=list)


class ActiveProviderRequest(BaseModel):
    provider_id: str


class ActiveProviderResponse(BaseModel):
    provider_id: str
    provider: ProviderProfileSchema | None = None


class ProviderTestResponse(BaseModel):
    provider_id: str
    status: str
    latency_ms: int
    warnings: list[str] = Field(default_factory=list)
    models: list[str] = Field(default_factory=list)
    detail: str = ""


class AppSettings(BaseModel):
    llm_provider: str = "deterministic_baseline"
    model: str = "local-keyword"
    temperature: float = 0.0
    active_model_provider: str = "deterministic_baseline"
