from __future__ import annotations

import hashlib
from typing import Any

from argument_risk_engine.classification.deterministic import classify_deterministic
from argument_risk_engine.explanation.explainer import explain_risk, false_positive_warning
from argument_risk_engine.extraction.claim_extractor import Claim, extract_claims
from argument_risk_engine.retrieval.lexical_retriever import RetrievedTaxonomyEntry, retrieve_candidates
from argument_risk_engine.scoring.calibration import risk_level
from argument_risk_engine.scoring.scorer import score_classification
from argument_risk_engine.taxonomy.models import TaxonomyEntry, TaxonomyPack, default_taxonomy_pack

DEFAULT_MODE = "deterministic_baseline"
DEFAULT_MODEL_PROVIDER_ID = "deterministic_baseline"
DEFAULT_MODEL_NAME = "local-keyword-v1"


def analyze_text(
    text: str,
    pack: TaxonomyPack | None = None,
    *,
    mode: str = DEFAULT_MODE,
    model_provider_id: str = DEFAULT_MODEL_PROVIDER_ID,
    top_k: int = 8,
    include_healthy_patterns: bool = True,
    max_risks_per_claim: int = 3,
    allow_deterministic_fallback: bool = True,
    include_retrieval_diagnostics: bool = False,
) -> dict[str, Any]:
    taxonomy_pack = pack or default_taxonomy_pack()
    normalized_text = text or ""
    claims = extract_claims(normalized_text)
    claims_out: list[dict[str, Any]] = []
    all_scores: list[float] = []
    warnings: list[str] = []
    any_review = False

    for index, claim in enumerate(claims, start=1):
        candidates = retrieve_candidates(str(claim), taxonomy_pack, limit=top_k)
        classified = classify_deterministic(
            str(claim),
            candidates,
            context=_context_for_claim(normalized_text, claim),
            classification_mode=mode,
            model_provider_id=model_provider_id,
            model_name=DEFAULT_MODEL_NAME,
            deterministic_fallback_used=False,
        )
        candidate_by_id = {candidate.entry.id: candidate for candidate in candidates}
        high_confidence_count = 0
        detected: list[dict[str, Any]] = []
        claim_warnings: list[str] = []

        for classification in classified:
            entry = _entry_by_id(taxonomy_pack, str(classification.get("taxonomy_id") or classification.get("risk_id")))
            if entry is None:
                continue
            candidate = candidate_by_id.get(entry.id)
            classification = dict(classification)
            classification["claim_type"] = claim.claim_type
            classification = _absolute_evidence(classification, claim, normalized_text)
            scored = score_classification(
                classification,
                entry=entry,
                candidate=candidate,
                claim_text=str(claim),
                has_context=len(claims) > 1,
                high_confidence_risk_count=high_confidence_count,
            )
            if scored.suppressed:
                if scored.warning:
                    claim_warnings.append(scored.warning)
                continue
            if float(classification.get("confidence", 0.0) or 0.0) >= 0.75:
                high_confidence_count += 1
            review = bool(scored.needs_human_review or entry.requires_human_judgment)
            any_review = any_review or review
            warning = false_positive_warning(entry, scored.warning or str(classification.get("false_positive_warning", "") or ""))
            risk = {
                "risk_id": entry.id,
                "category": entry.canonical_category,
                "label": entry.name,
                "severity": classification.get("severity", entry.severity.value),
                "confidence": round(float(classification.get("confidence", 0.0) or 0.0), 3),
                "risk_score": scored.risk_score,
                "risk_level": scored.risk_level,
                "evidence_span": classification.get("evidence_span", ""),
                "evidence_start_char": classification.get("evidence_start_char", claim.start_char),
                "evidence_end_char": classification.get("evidence_end_char", claim.end_char),
                "explanation": explain_risk(entry, classification, scored.risk_score, scored.risk_level),
                "false_positive_warning": warning,
                "needs_human_review": review,
            }
            detected.append(risk)
            all_scores.append(scored.risk_score)

        detected.sort(key=lambda item: (-float(item["risk_score"]), str(item["risk_id"])))
        detected = detected[: max(0, max_risks_per_claim)]
        diagnostics = _diagnostics(candidates) if include_retrieval_diagnostics else {}
        claims_out.append(
            {
                "claim_id": f"claim_{index}",
                "text": claim.text,
                "claim_type": claim.claim_type,
                "start_char": claim.start_char,
                "end_char": claim.end_char,
                "detected_risks": detected,
                "healthy_patterns": _healthy_patterns(candidates) if include_healthy_patterns else [],
                "warnings": sorted(set(claim_warnings)),
                "retrieval_diagnostics": diagnostics,
            }
        )

    overall = round(max(all_scores) if all_scores else 0.0, 3)
    return {
        "text_id": _stable_text_id(normalized_text),
        "mode": mode,
        "model_provider_id": model_provider_id,
        "model_name": DEFAULT_MODEL_NAME,
        "llm_used": False,
        "deterministic_fallback_used": False if mode == DEFAULT_MODE else allow_deterministic_fallback,
        "claims": claims_out,
        "overall_risk_score": overall,
        "risk_level": risk_level(overall),
        "needs_human_review": any_review,
        "warnings": warnings,
        # Backwards-compatible summary fields for older callers/tests.
        "analysis_id": _stable_text_id(normalized_text),
        "summary": {
            "claim_count": len(claims_out),
            "risk_count": sum(len(claim["detected_risks"]) for claim in claims_out),
            "highest_severity": _highest_severity([risk for claim in claims_out for risk in claim["detected_risks"]]),
            "stance": "conservative_review_signal",
        },
        "risks": [risk for claim in claims_out for risk in claim["detected_risks"]],
    }


def _stable_text_id(text: str) -> str:
    return "txt_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _entry_by_id(pack: TaxonomyPack, entry_id: str) -> TaxonomyEntry | None:
    return next((entry for entry in pack.entries if entry.id == entry_id), None)


def _context_for_claim(text: str, claim: Claim) -> str:
    before = text[max(0, claim.start_char - 400) : claim.start_char].strip()
    after = text[claim.end_char : min(len(text), claim.end_char + 400)].strip()
    return "\n".join(part for part in (before, after) if part)


def _absolute_evidence(classification: dict[str, Any], claim: Claim, text: str) -> dict[str, Any]:
    span = str(classification.get("evidence_span", "") or "")
    rel_start = int(classification.get("evidence_start_char", 0) or 0)
    rel_end = int(classification.get("evidence_end_char", rel_start + len(span)) or rel_start + len(span))
    abs_start = claim.start_char + rel_start if 0 <= rel_start <= len(claim.text) else text.find(span)
    abs_end = abs_start + len(span) if abs_start >= 0 else claim.start_char + rel_end
    exact = bool(span and abs_start >= 0 and text[abs_start:abs_end] == span)
    if not exact and span:
        found = text.find(span)
        if found >= 0:
            abs_start = found
            abs_end = found + len(span)
            exact = True
    classification["evidence_start_char"] = max(0, abs_start)
    classification["evidence_end_char"] = max(0, abs_end)
    classification["evidence_exact"] = exact
    return classification


def _healthy_patterns(candidates: list[RetrievedTaxonomyEntry]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    patterns: list[dict[str, Any]] = []
    for candidate in candidates:
        for pattern_id in candidate.healthy_pattern_matches:
            if pattern_id not in seen:
                seen.add(pattern_id)
                patterns.append({"pattern_id": pattern_id, "effect": "suppressed_or_reduced_risk"})
    return patterns


def _diagnostics(candidates: list[RetrievedTaxonomyEntry]) -> dict[str, Any]:
    return candidates[0].diagnostics if candidates else {}


def _highest_severity(risks: list[dict[str, Any]]) -> str:
    order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    highest = "none"
    for risk in risks:
        severity = str(risk.get("severity", "none"))
        if order.get(severity, 0) > order[highest]:
            highest = severity
    return highest
