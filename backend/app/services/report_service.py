from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from argument_risk_engine.reports.html import render_html_report
from argument_risk_engine.reports.json_export import render_json_report
from argument_risk_engine.reports.markdown import render_markdown_report

from backend.app.core.paths import REPORTS_DIR
from backend.app.services.analyzer_service import analyze

INDEX_PATH = REPORTS_DIR / "reports_index.json"
SUPPORTED_FORMATS = {"json", "markdown", "html"}


def create_report_from_analysis(analysis: dict[str, Any], title: str = "Argument Risk Report", formats: list[str] | None = None) -> dict[str, Any]:
    requested = [fmt for fmt in (formats or ["json", "markdown", "html"]) if fmt in SUPPORTED_FORMATS]
    if not requested:
        requested = ["json"]
    report_id = f"rpt_{uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    analysis_id = str(analysis.get("analysis_id") or analysis.get("text_id") or "unknown")
    payload: dict[str, Any] = {
        "report_id": report_id,
        "title": title,
        "created_at": created_at,
        "analysis_id": analysis_id,
        "formats": requested,
    }
    if "json" in requested:
        payload["json"] = render_json_report(analysis)
    if "markdown" in requested:
        payload["markdown"] = render_markdown_report(analysis)
    if "html" in requested:
        payload["html"] = render_html_report(analysis)
    _write_report(payload)
    _append_index({key: payload[key] for key in ("report_id", "title", "created_at", "analysis_id", "formats")})
    return payload


def list_reports() -> list[dict[str, Any]]:
    return _read_index()


def get_report(report_id: str) -> dict[str, Any] | None:
    path = _report_path(report_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def get_report_content(report_id: str, report_format: str) -> tuple[str, str, str] | None:
    report = get_report(report_id)
    if not report or report_format not in SUPPORTED_FORMATS or not report.get(report_format):
        return None
    extension = "md" if report_format == "markdown" else report_format
    media_type = {"json": "application/json", "markdown": "text/markdown", "html": "text/html"}[report_format]
    return str(report[report_format]), media_type, f"{report_id}.{extension}"


def demo_report() -> str:
    return render_markdown_report(analyze("Everyone always caused this problem."))


def _write_report(report: dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _report_path(str(report["report_id"])).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _report_path(report_id: str) -> Path:
    safe = "".join(char for char in report_id if char.isalnum() or char in {"_", "-"})
    return REPORTS_DIR / f"{safe}.json"


def _read_index() -> list[dict[str, Any]]:
    if not INDEX_PATH.exists():
        return []
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _append_index(summary: dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    records = [item for item in _read_index() if item.get("report_id") != summary["report_id"]]
    records.insert(0, summary)
    INDEX_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
