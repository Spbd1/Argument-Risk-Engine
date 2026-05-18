from __future__ import annotations

from argument_risk_engine.retrieval.candidate_filter import is_healthy_suppressor
from argument_risk_engine.taxonomy.models import ActivationStatus, TaxonomyEntry

MAX_RISKS_PER_SHORT_CLAIM = 3
SHORT_CLAIM_CHAR_LIMIT = 280


def classify_deterministic(
    claim: str,
    candidates: list[TaxonomyEntry] | list[object],
    *,
    context: str = "",
    classification_mode: str = "deterministic_baseline",
    model_provider_id: str = "deterministic_baseline",
    model_name: str = "local-keyword",
    deterministic_fallback_used: bool = False,
) -> list[dict[str, object]]:
    """Conservatively classify retrieved candidates without network access.

    The deterministic baseline only emits taxonomy-grounded risks when an active,
    classification-enabled candidate has an exact textual evidence span in the
    claim/context and no false-positive guard dominates the match.
    """

    haystack = _evidence_haystack(claim, context)
    healthy_dominates = _healthy_suppressor_dominates(candidates)
    results: list[dict[str, object]] = []

    for candidate in candidates:
        entry = _entry(candidate)
        if not _is_classifiable(entry):
            continue
        if is_healthy_suppressor(entry):
            continue
        if healthy_dominates and _candidate_false_positive_risk(candidate) == "high":
            continue
        if _exclusion_triggered(haystack, entry.exclusion_criteria):
            continue

        evidence = _best_evidence_span(haystack, entry, candidate)
        if evidence is None:
            continue

        start, end, span, matched_terms = evidence
        confidence = _confidence(candidate, matched_terms, entry)
        if confidence < _minimum_confidence(entry):
            continue

        results.append(
            {
                "risk_id": entry.id,
                "taxonomy_id": entry.id,  # backwards-compatible alias
                "category": entry.canonical_category,
                "label": entry.name,
                "severity": _severity(entry, confidence),
                "confidence": confidence,
                "evidence_span": span,
                "evidence_start_char": start,
                "evidence_end_char": end,
                "explanation": _explanation(entry, matched_terms, confidence),
                "false_positive_warning": _false_positive_warning(entry, candidate),
                "classification_mode": classification_mode,
                "model_provider_id": model_provider_id,
                "model_name": model_name,
                "llm_used": False,
                "deterministic_fallback_used": deterministic_fallback_used,
                "insufficient_evidence": False,
                "matched_terms": matched_terms,
            }
        )

    results.sort(key=lambda item: (-float(item["confidence"]), str(item["risk_id"])))
    limit = MAX_RISKS_PER_SHORT_CLAIM if len(claim) <= SHORT_CLAIM_CHAR_LIMIT else len(results)
    return results[:limit]


def _entry(candidate: object) -> TaxonomyEntry:
    return getattr(candidate, "entry", candidate)


def _is_classifiable(entry: TaxonomyEntry) -> bool:
    return bool(
        entry.enabled_for_classification
        and entry.activation_status == ActivationStatus.active.value
        and not is_healthy_suppressor(entry)
    )


def _evidence_haystack(claim: str, context: str = "") -> str:
    return claim if not context else f"{claim}\n{context}"


def _healthy_suppressor_dominates(candidates: list[object]) -> bool:
    for candidate in candidates:
        entry = _entry(candidate)
        if is_healthy_suppressor(entry):
            score = float(getattr(candidate, "retrieval_score", 0.0) or 0.0)
            if score >= 1.0:
                return True
        diagnostics = getattr(candidate, "diagnostics", {}) or {}
        if int(diagnostics.get("healthy_suppressor_count", 0) or 0) > 0 and _candidate_false_positive_risk(candidate) == "high":
            return True
    return False


def _candidate_false_positive_risk(candidate: object) -> str:
    return str(getattr(candidate, "false_positive_risk", "medium") or "medium")


def _exclusion_triggered(text: str, exclusions: list[str]) -> bool:
    lower = text.lower()
    return any(exclusion.strip() and exclusion.lower() in lower for exclusion in exclusions)


def _best_evidence_span(text: str, entry: TaxonomyEntry, candidate: object) -> tuple[int, int, str, list[str]] | None:
    terms = _candidate_terms(entry, candidate)
    matches: list[tuple[int, int, str]] = []
    lower = text.lower()
    for term in terms:
        needle = term.strip()
        if not needle:
            continue
        start = lower.find(needle.lower())
        if start >= 0:
            end = start + len(needle)
            matches.append((start, end, text[start:end]))
    if not matches:
        return None

    matches.sort(key=lambda item: (-(item[1] - item[0]), item[0]))
    start, end, span = matches[0]
    matched_terms = sorted({match[2] for match in matches}, key=lambda item: item.lower())
    return start, end, span, matched_terms


def _candidate_terms(entry: TaxonomyEntry, candidate: object) -> list[str]:
    terms: list[str] = []
    terms.extend(str(term) for term in getattr(candidate, "matched_terms", []) or [])
    terms.extend(entry.signals)
    terms.extend(entry.trigger_patterns)
    return sorted({term.strip() for term in terms if term and str(term).strip()}, key=len, reverse=True)


def _confidence(candidate: object, matched_terms: list[str], entry: TaxonomyEntry) -> float:
    score = float(getattr(candidate, "retrieval_score", 0.0) or 0.0)
    if score > 0:
        confidence = min(0.92, 0.42 + (score * 0.12) + (0.04 * len(matched_terms)))
    else:
        confidence = min(0.86, 0.45 + (0.15 * len(matched_terms)))
    if entry.requires_context or entry.requires_human_judgment:
        confidence -= 0.12
    if _candidate_false_positive_risk(candidate) == "high":
        confidence -= 0.10
    return round(max(0.0, confidence), 3)


def _minimum_confidence(entry: TaxonomyEntry) -> float:
    if entry.requires_context or entry.false_positive_sensitivity == "high":
        return 0.62
    return 0.50


def _severity(entry: TaxonomyEntry, confidence: float) -> str:
    severity = entry.severity.value
    if severity == "high" and confidence < 0.58:
        return "medium"
    return severity


def _explanation(entry: TaxonomyEntry, matched_terms: list[str], confidence: float) -> str:
    terms = ", ".join(matched_terms[:4]) if matched_terms else "the cited evidence"
    return f"Matched {entry.name} using exact evidence ({terms}) with conservative confidence {confidence:.2f}."


def _false_positive_warning(entry: TaxonomyEntry, candidate: object) -> str:
    warnings: list[str] = []
    if entry.common_false_positives:
        warnings.append("Common false positives: " + "; ".join(entry.common_false_positives[:2]))
    if _candidate_false_positive_risk(candidate) == "high":
        warnings.append("High false-positive risk; human review recommended.")
    return " ".join(warnings)
