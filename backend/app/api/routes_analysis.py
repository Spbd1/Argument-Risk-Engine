from __future__ import annotations

from backend.app.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.app.services.analyzer_service import analyze
from fastapi import APIRouter

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_endpoint(request: AnalysisRequest) -> dict[str, object]:
    return analyze(request)


@router.post("/analysis/analyze", response_model=AnalysisResponse)
def analyze_legacy_endpoint(request: AnalysisRequest) -> dict[str, object]:
    return analyze(request)
