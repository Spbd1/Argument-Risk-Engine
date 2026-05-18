from backend.app.main import app
from fastapi.testclient import TestClient


def test_api_settings():
    client = TestClient(app)
    response = client.put("/api/settings", json={"llm_provider": "deterministic", "model": "local-keyword", "temperature": 0})
    assert response.status_code == 200
    assert response.json()["llm_provider"] == "deterministic"
