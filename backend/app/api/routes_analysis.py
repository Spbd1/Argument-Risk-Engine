from backend.app.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.app.services.analyzer_service import analyze
from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_endpoint(request: AnalysisRequest) -> dict[str, object]:
    return analyze(request.text)
