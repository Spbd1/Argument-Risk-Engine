from backend.app.main import app
from fastapi.testclient import TestClient


def test_api_settings():
    client = TestClient(app)
    response = client.put("/api/settings", json={"llm_provider": "deterministic", "model": "local-keyword", "temperature": 0})
    assert response.status_code == 200
    assert response.json()["llm_provider"] == "deterministic"


def test_model_provider_defaults_and_deterministic_test():
    client = TestClient(app)
    response = client.get("/api/settings/model-providers")
    assert response.status_code == 200
    providers = response.json()["providers"]
    provider_ids = {provider["provider_id"] for provider in providers}
    assert "deterministic_baseline" in provider_ids
    assert "lm_studio_local" in provider_ids
    assert "ollama_local" in provider_ids
    assert "openai_remote" in provider_ids
    assert all("api_key" not in provider for provider in providers)

    test_response = client.post("/api/settings/model-providers/deterministic_baseline/test")
    assert test_response.status_code == 200
    assert test_response.json()["status"] == "ok"


def test_active_provider_selection_and_secret_metadata_only():
    client = TestClient(app)
    select_response = client.post("/api/settings/active-model-provider", json={"provider_id": "lm_studio_local"})
    assert select_response.status_code == 200
    assert select_response.json()["provider_id"] == "lm_studio_local"

    patch_response = client.patch(
        "/api/settings/model-providers/lm_studio_local",
        json={"api_key_env_var": "LM_STUDIO_API_KEY", "api_key": "should-not-be-stored"},
    )
    assert patch_response.status_code == 200
    payload = patch_response.json()
    assert payload["api_key_env_var"] == "LM_STUDIO_API_KEY"
    assert "should-not-be-stored" not in str(payload)

    client.post("/api/settings/active-model-provider", json={"provider_id": "deterministic_baseline"})
