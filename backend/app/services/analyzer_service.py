from __future__ import annotations

from typing import Any

from argument_risk_engine.analyzer import analyze_text

from backend.app.schemas.analysis import AnalysisRequest
from backend.app.services.taxonomy_service import get_active_pack


def analyze(request: AnalysisRequest | str) -> dict[str, Any]:
    if isinstance(request, str):
        return analyze_text(request, get_active_pack())
    return analyze_text(
        request.text,
        get_active_pack(),
        mode=request.mode,
        model_provider_id=request.model_provider_id,
        top_k=int(request.top_k),
        include_healthy_patterns=bool(request.include_healthy_patterns),
        max_risks_per_claim=int(request.max_risks_per_claim),
        allow_deterministic_fallback=bool(request.allow_deterministic_fallback),
        include_retrieval_diagnostics=bool(request.include_retrieval_diagnostics),
    )
