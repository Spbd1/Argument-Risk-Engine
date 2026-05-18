from __future__ import annotations

from backend.app.schemas.reports import ReportFromAnalysisRequest
from backend.app.services.report_service import (
    create_report_from_analysis,
    demo_report,
    get_report,
    get_report_content,
    list_reports,
)
from fastapi import APIRouter, Response

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/from-analysis")
def from_analysis(payload: ReportFromAnalysisRequest) -> dict[str, object]:
    return create_report_from_analysis(payload.analysis, payload.title, payload.formats)


@router.get("")
def reports() -> list[dict[str, object]]:
    return list_reports()


@router.get("/")
def reports_slash() -> list[dict[str, object]]:
    return list_reports()


@router.get("/{report_id}")
def report_detail(report_id: str) -> dict[str, object]:
    report = get_report(report_id)
    return report or {"detail": "not found"}


@router.get("/{report_id}/download")
def report_download(report_id: str, format: str = "markdown") -> Response:
    content = get_report_content(report_id, format)
    if content is None:
        return Response(content="Report or format not found", media_type="text/plain", status_code=404)
    body, media_type, filename = content
    return Response(content=body, media_type=media_type, headers={"content-disposition": f'attachment; filename="{filename}"'})


@router.get("/demo.md")
def report_demo() -> Response:
    return Response(content=demo_report(), media_type="text/markdown")
