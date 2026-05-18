from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReportFromAnalysisRequest(BaseModel):
    analysis: dict[str, Any]
    title: str = "Argument Risk Report"
    formats: list[str] = Field(default_factory=lambda: ["json", "markdown", "html"])


class ReportSummary(BaseModel):
    report_id: str
    title: str
    created_at: str
    analysis_id: str
    formats: list[str]


class ReportResponse(BaseModel):
    report_id: str
    title: str
    created_at: str
    analysis_id: str
    formats: list[str]
    json: str | None = None
    markdown: str | None = None
    html: str | None = None
