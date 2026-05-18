from argument_risk_engine.analyzer import analyze_text

from backend.app.services.taxonomy_service import get_active_pack


def analyze(text: str) -> dict[str, object]:
    return analyze_text(text, get_active_pack())
