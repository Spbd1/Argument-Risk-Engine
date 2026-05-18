from __future__ import annotations

from typing import Any

from argument_risk_engine.taxonomy.models import TaxonomyEntry


def explain(entry: TaxonomyEntry, matched_terms: list[str]) -> str:
    terms = ", ".join(matched_terms) if matched_terms else "taxonomy language"
    return f"Matched {entry.name} because the claim contains {terms}. This is a review signal, not a truth judgement."


def explain_risk(entry: TaxonomyEntry, classification: dict[str, Any], risk_score: float, risk_level: str) -> str:
    evidence = str(classification.get("evidence_span", "the cited text") or "the cited text")
    definition = entry.short_definition or entry.long_definition or entry.name
    return (
        f"The evidence span {evidence!r} matches {entry.name}: {definition} "
        f"The calibrated score is {risk_score:.2f} ({risk_level}); this flags argument risk, not factual truth."
    )


def false_positive_warning(entry: TaxonomyEntry, extra_warning: str = "") -> str:
    parts: list[str] = []
    if entry.common_false_positives:
        parts.append("Check false positives: " + "; ".join(entry.common_false_positives[:2]) + ".")
    if entry.requires_human_judgment:
        parts.append("This category may require human judgment.")
    if extra_warning:
        parts.append(extra_warning)
    return " ".join(parts)
