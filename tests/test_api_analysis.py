from backend.app.main import app
from fastapi.testclient import TestClient


REQUEST = {
    "text": "Everyone always caused this.",
    "mode": "deterministic_baseline",
    "model_provider_id": "deterministic_baseline",
    "top_k": 8,
    "include_healthy_patterns": True,
    "max_risks_per_claim": 3,
    "allow_deterministic_fallback": True,
    "include_retrieval_diagnostics": False,
}


def test_health_endpoint():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_analyze_endpoint_without_api_key():
    response = TestClient(app).post("/analyze", json=REQUEST)
    body = response.json()

    assert response.status_code == 200
    assert body["text_id"].startswith("txt_")
    assert body["llm_used"] is False
    assert body["claims"][0]["detected_risks"]


def test_api_analyze_endpoint_without_api_key():
    response = TestClient(app).post("/api/analyze", json=REQUEST)

    assert response.status_code == 200
    assert response.json()["claims"][0]["detected_risks"]


def test_legacy_analysis_endpoint_still_works():
    response = TestClient(app).post("/api/analysis/analyze", json={"text": "Everyone always caused this."})

    assert response.status_code == 200
    assert response.json()["claims"][0]["detected_risks"]
