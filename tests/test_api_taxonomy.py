from backend.app.main import app
from fastapi.testclient import TestClient


def test_api_taxonomy():
    response = TestClient(app).get("/api/taxonomy")
    assert response.status_code == 200
    assert response.json()["entries"]
