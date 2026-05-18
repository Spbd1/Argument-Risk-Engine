from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from argument_risk_engine.classification.model_provider import ProviderProfile
from pydantic import BaseModel


class ProviderTestResult(BaseModel):
    provider_id: str
    status: str
    latency_ms: int
    warnings: list[str]
    models: list[str]
    detail: str = ""


class LLMClient:
    def __init__(self, profile: ProviderProfile | None = None):
        self.profile = profile

    def classify(self, prompt: str) -> dict[str, str]:
        provider_id = self.profile.provider_id if self.profile else "deterministic_baseline"
        return {"provider": provider_id, "response": "LLM providers are optional; deterministic baseline is available."}

    def test_provider(self) -> ProviderTestResult:
        if self.profile is None or self.profile.provider_type == "deterministic":
            provider_id = self.profile.provider_id if self.profile else "deterministic_baseline"
            return ProviderTestResult(provider_id=provider_id, status="ok", latency_ms=0, warnings=[], models=[], detail="Deterministic provider is available offline.")
        return test_openai_compatible_provider(self.profile)


def test_openai_compatible_provider(profile: ProviderProfile) -> ProviderTestResult:
    start = time.perf_counter()
    warnings: list[str] = []
    models: list[str] = []

    if not profile.base_url:
        return _result(profile, "not_configured", start, ["base_url is required for OpenAI-compatible providers."], models)

    api_key = os.environ.get(profile.api_key_env_var, "") if profile.api_key_env_var else ""
    if profile.api_key_env_var and not api_key:
        warnings.append(f"Environment variable {profile.api_key_env_var} is not set; local providers may still accept unauthenticated requests.")

    models_status, model_warning, models = _get_models(profile, api_key)
    if models_status == "ok":
        return _result(profile, "ok", start, warnings, models, "Fetched /models successfully.")
    if model_warning:
        warnings.append(model_warning)

    chat_status, chat_warning = _minimal_chat_completion(profile, api_key)
    if chat_status == "ok":
        return _result(profile, "ok", start, warnings, models, "Minimal chat completion succeeded.")
    if chat_warning:
        warnings.append(chat_warning)
    return _result(profile, "failed", start, warnings, models)


def _get_models(profile: ProviderProfile, api_key: str) -> tuple[str, str, list[str]]:
    url = _join_url(profile.base_url, "models")
    status, payload, warning = _request_json("GET", url, api_key, None, profile.timeout_seconds)
    if status != "ok":
        return status, warning, []
    data = payload.get("data", payload if isinstance(payload, list) else [])
    models = [str(item.get("id", item)) for item in data if item]
    return "ok", "", models


def _minimal_chat_completion(profile: ProviderProfile, api_key: str) -> tuple[str, str]:
    if not profile.model_name:
        return "not_configured", "model_name is required to test chat completions."
    body = {
        "model": profile.model_name,
        "messages": [{"role": "user", "content": "Return ok."}],
        "max_tokens": 8,
        "temperature": 0,
        "stream": False,
    }
    url = _join_url(profile.base_url, "chat/completions")
    status, _payload, warning = _request_json("POST", url, api_key, body, profile.timeout_seconds)
    return status, warning


def _request_json(method: str, url: str, api_key: str, body: dict[str, Any] | None, timeout: int) -> tuple[str, dict[str, Any] | list[Any], str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=max(1, int(timeout or 30))) as response:
            raw = response.read().decode("utf-8")
            return "ok", json.loads(raw) if raw else {}, ""
    except HTTPError as exc:
        return "failed", {}, f"{method} {url} returned HTTP {exc.code}."
    except URLError as exc:
        return "failed", {}, f"{method} {url} could not connect: {exc.reason}."
    except TimeoutError:
        return "failed", {}, f"{method} {url} timed out."
    except json.JSONDecodeError:
        return "failed", {}, f"{method} {url} returned invalid JSON."


def _join_url(base_url: str, suffix: str) -> str:
    return f"{base_url.rstrip('/')}/{suffix.lstrip('/')}"


def _result(profile: ProviderProfile, status: str, start: float, warnings: list[str], models: list[str], detail: str = "") -> ProviderTestResult:
    return ProviderTestResult(
        provider_id=profile.provider_id,
        status=status,
        latency_ms=int((time.perf_counter() - start) * 1000),
        warnings=warnings,
        models=models,
        detail=detail,
    )
