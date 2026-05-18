from __future__ import annotations

from uuid import uuid4

from argument_risk_engine.classification.deterministic import classify_deterministic
from argument_risk_engine.explanation.evidence import evidence_span
from argument_risk_engine.explanation.explainer import explain
from argument_risk_engine.extraction.claim_extractor import extract_claims
from argument_risk_engine.retrieval.lexical_retriever import retrieve_candidates
from argument_risk_engine.scoring.scorer import score_risk
from argument_risk_engine.taxonomy.models import TaxonomyPack, default_taxonomy_pack


def analyze_text(text: str, pack: TaxonomyPack | None = None) -> dict[str, object]:
    taxonomy_pack = pack or default_taxonomy_pack()
    claims_out: list[dict[str, object]] = []
    all_risks: list[dict[str, object]] = []
    for claim in extract_claims(text):
        candidates = retrieve_candidates(claim, taxonomy_pack)
        classified = classify_deterministic(claim, candidates)
        risks: list[dict[str, object]] = []
        for result in classified:
            entry = next(item for item in taxonomy_pack.entries if item.id == result["taxonomy_id"])
            risk = {
                "taxonomy_id": entry.id,
                "name": entry.name,
                "severity": entry.severity.value,
                "confidence": result["confidence"],
                "score": score_risk(entry.severity.value, float(result["confidence"])),
                "explanation": explain(entry, list(result["matched_terms"])),
                "evidence": evidence_span(text, claim),
                "mitigation": entry.mitigation,
            }
            risks.append(risk)
            all_risks.append(risk)
        claims_out.append({"text": claim, "risks": risks})
    return {
        "analysis_id": str(uuid4()),
        "summary": {
            "claim_count": len(claims_out),
            "risk_count": len(all_risks),
            "highest_severity": _highest_severity(all_risks),
            "stance": "conservative_review_signal",
        },
        "claims": claims_out,
        "risks": all_risks,
    }


def _highest_severity(risks: list[dict[str, object]]) -> str:
    order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    highest = "none"
    for risk in risks:
        severity = str(risk.get("severity", "none"))
        if order.get(severity, 0) > order[highest]:
            highest = severity
    return highest
