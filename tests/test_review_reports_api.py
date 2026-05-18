from __future__ import annotations

from backend.app.main import app
from fastapi.testclient import TestClient


def test_review_items_endpoint_records_item(tmp_path, monkeypatch):
    from backend.app.services import review_service

    monkeypatch.setattr(review_service, "REVIEW_STORE_PATH", tmp_path / "review_store.jsonl")
    client = TestClient(app)
    response = client.post(
        "/api/review/items",
        json={
            "text_id": "txt_test",
            "claim_id": "claim_1",
            "claim_text": "They are vermin.",
            "predicted_risks": [{"risk_id": "dehumanizing_language"}],
            "reviewer_decision": "correct",
            "corrected_labels": ["dehumanizing_language"],
            "corrected_evidence_spans": ["vermin"],
            "reviewer_notes": "ok",
        },
    )

    assert response.status_code == 200
    assert response.json()["review_id"].startswith("rev_")
    assert client.get("/api/review/summary").json()["total_reviews"] == 1


def test_evaluation_and_reports_endpoints(tmp_path, monkeypatch):
    from backend.app.services import evaluation_service, report_service

    monkeypatch.setattr(evaluation_service, "EVALUATION_RESULT_PATH", tmp_path / "last_evaluation.json")
    monkeypatch.setattr(report_service, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(report_service, "INDEX_PATH", tmp_path / "reports" / "reports_index.json")
    client = TestClient(app)
    evaluation = client.post("/api/evaluation/run", json={}).json()

    assert evaluation["items"] >= 1
    assert "label_f1" in evaluation["metrics"]

    analysis = evaluation["analyses"][0]
    report = client.post(
        "/api/reports/from-analysis",
        json={"analysis": analysis, "title": "Smoke report", "formats": ["json", "markdown", "html"]},
    ).json()

    assert report["report_id"].startswith("rpt_")
    assert "Argument Risk Report" in report["markdown"]
    download = client.get(f"/api/reports/{report['report_id']}/download?format=markdown")
    assert download.status_code == 200
    assert "Argument Risk Report" in download.content
