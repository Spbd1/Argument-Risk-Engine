from __future__ import annotations

import json
from typing import Any

CLASSIFICATION_SYSTEM_PROMPT = """You are a taxonomy-grounded argument risk classifier.
Return strict JSON only. Do not include markdown, prose, or comments.

Rules:
- Use only candidate taxonomy entries supplied in the prompt.
- Do not invent taxonomy labels, IDs, categories, or severities.
- Do not determine factual truth.
- Do not judge author intent.
- Do not classify personality or psychology.
- Do not classify without textual evidence.
- Evidence spans must be exact substrings of the claim or context.
- Prefer insufficient_evidence when uncertain.
"""

CLASSIFICATION_PROMPT = CLASSIFICATION_SYSTEM_PROMPT


def build_classification_prompt(claim: str, context: str, candidates: list[object]) -> str:
    payload = {
        "task": "classify_argument_risks",
        "claim": claim,
        "context": context,
        "candidate_taxonomy_entries": [_candidate_payload(candidate) for candidate in candidates],
        "required_json_schema": {
            "assessments": [
                {
                    "risk_id": "candidate id only",
                    "category": "candidate canonical_category only",
                    "label": "candidate name only",
                    "severity": "low|medium|high from candidate guidance only",
                    "confidence": "number 0..1",
                    "evidence_span": "exact substring of claim or context",
                    "explanation": "brief taxonomy-grounded reason",
                    "false_positive_warning": "brief warning or empty string",
                    "insufficient_evidence": "boolean",
                }
            ],
            "warning": "optional warning string",
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_messages(claim: str, context: str, candidates: list[object]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
        {"role": "user", "content": build_classification_prompt(claim, context, candidates)},
    ]


def _candidate_payload(candidate: object) -> dict[str, Any]:
    entry = getattr(candidate, "entry", candidate)
    return {
        "id": entry.id,
        "name": entry.name,
        "canonical_category": entry.canonical_category,
        "short_definition": entry.short_definition,
        "minimum_evidence_requirement": entry.minimum_evidence_requirement,
        "signals": entry.signals,
        "trigger_patterns": entry.trigger_patterns,
        "exclusion_criteria": entry.exclusion_criteria,
        "common_false_positives": entry.common_false_positives,
        "severity": entry.severity.value,
        "severity_guidance": entry.severity_guidance,
        "retrieval_score": getattr(candidate, "retrieval_score", None),
        "matched_terms": getattr(candidate, "matched_terms", []),
    }
