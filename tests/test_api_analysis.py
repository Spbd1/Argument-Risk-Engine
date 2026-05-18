from backend.app.main import app
from fastapi.testclient import TestClient


def test_api_analysis():
    response = TestClient(app).post("/api/analysis/analyze", json={"text": "Everyone always caused this."})
    assert response.status_code == 200
    assert response.json()["risks"]
