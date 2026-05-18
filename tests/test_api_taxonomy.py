from backend.app.main import app
from fastapi.testclient import TestClient


def test_api_taxonomy():
    response = TestClient(app).get("/api/taxonomy")
    assert response.status_code == 200
    assert response.json()["entries"]


def test_taxonomy_lookup_search_and_summary():
    client = TestClient(app)
    entries = client.get("/api/taxonomy").json()["entries"]
    risk_id = entries[0]["id"]

    detail = client.get(f"/api/taxonomy/{risk_id}")
    assert detail.status_code == 200
    assert detail.json()["entry"]["id"] == risk_id

    search = client.get(f"/api/taxonomy/search?q={risk_id}")
    assert search.status_code == 200
    assert search.json()["entries"]

    categories = client.get("/api/taxonomy/categories")
    assert categories.status_code == 200
    assert categories.json()["categories"]

    summary = client.get("/api/taxonomy/summary")
    assert summary.status_code == 200
    assert summary.json()["entry_count"] >= len(entries)


def test_taxonomy_workbench_reports_and_export():
    client = TestClient(app)
    assert client.get("/api/taxonomy-workbench/packs").json()["packs"]
    assert client.get("/api/taxonomy-workbench/coverage").json()["entry_count"] > 0
    assert "warnings" in client.get("/api/taxonomy-workbench/quality-report").json()
    assert "errors" in client.post("/api/taxonomy-workbench/validate").json()

    export = client.get("/api/taxonomy-workbench/export-excel")
    assert export.status_code == 200
    assert export.content
    assert export.headers["Content-Disposition"].endswith('.xlsx"')
