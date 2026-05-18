from __future__ import annotations

import json
from typing import Any, Literal

from argument_risk_engine.classification.deterministic import classify_deterministic
from argument_risk_engine.classification.llm_client import LLMClient, LLMClientError
from argument_risk_engine.classification.model_provider import ProviderProfile
from argument_risk_engine.classification.prompts import build_classification_prompt, build_messages
from argument_risk_engine.taxonomy.models import TaxonomyEntry
from pydantic import BaseModel, Field

ClassificationMode = Literal["deterministic_baseline", "llm"]


class RiskAssessment(BaseModel):
    risk_id: str
    category: str
    label: str
    severity: str
    confidence: float
    evidence_span: str
    evidence_start_char: int
    evidence_end_char: int
    explanation: str
    false_positive_warning: str = ""
    classification_mode: str
    model_provider_id: str
    model_name: str
    llm_used: bool
    deterministic_fallback_used: bool
    insufficient_evidence: bool = False


class ClassificationResult(BaseModel):
    assessments: list[RiskAssessment] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    model_error: str = ""
    classification_mode: str = "deterministic_baseline"
    model_provider_id: str = "deterministic_baseline"
    model_name: str = "local-keyword"
    llm_used: bool = False
    deterministic_fallback_used: bool = False


class ClassifierConfig(BaseModel):
    mode: ClassificationMode = "deterministic_baseline"
    fallback_to_deterministic: bool = True


class ArgumentRiskClassifier:
    """Taxonomy-grounded classification layer with offline and optional LLM modes."""

    def __init__(
        self,
        *,
        provider_profile: ProviderProfile | None = None,
        llm_client: LLMClient | None = None,
        config: ClassifierConfig | None = None,
    ):
        self.provider_profile = provider_profile
        self.config = config or ClassifierConfig(
            mode="llm" if provider_profile and provider_profile.provider_type != "deterministic" else "deterministic_baseline"
        )
        self.llm_client = llm_client or LLMClient(provider_profile)

    def classify_claim(self, claim: str, candidates: list[TaxonomyEntry] | list[object], *, context: str = "") -> ClassificationResult:
        if self.config.mode == "deterministic_baseline" or self.provider_profile is None or self.provider_profile.provider_type == "deterministic":
            return self._deterministic_result(claim, candidates, context=context, fallback=False)
        return self._llm_result(claim, candidates, context=context)

    def classify(self, claim: str, candidates: list[TaxonomyEntry] | list[object], *, context: str = "") -> list[RiskAssessment]:
        return self.classify_claim(claim, candidates, context=context).assessments

    def _deterministic_result(self, claim: str, candidates: list[object], *, context: str, fallback: bool, warning: str = "") -> ClassificationResult:
        provider_id = "deterministic_baseline"
        model_name = "local-keyword"
        assessments = [
            RiskAssessment(**item)
            for item in classify_deterministic(
                claim,
                candidates,
                context=context,
                classification_mode="deterministic_baseline",
                model_provider_id=provider_id,
                model_name=model_name,
                deterministic_fallback_used=fallback,
            )
        ]
        warnings = [warning] if warning else []
        return ClassificationResult(
            assessments=assessments,
            warnings=warnings,
            model_error=warning,
            classification_mode="deterministic_baseline",
            model_provider_id=provider_id,
            model_name=model_name,
            llm_used=False,
            deterministic_fallback_used=fallback,
        )

    def _llm_result(self, claim: str, candidates: list[object], *, context: str) -> ClassificationResult:
        profile = self.provider_profile
        assert profile is not None
        provider_id = profile.provider_id
        model_name = profile.model_name
        prompt = build_classification_prompt(claim, context, candidates)
        messages = build_messages(claim, context, candidates)
        try:
            raw = self.llm_client.classify(prompt, messages=messages)
            payload = _coerce_llm_payload(raw)
            assessments, warnings = _validate_llm_assessments(
                payload,
                claim=claim,
                context=context,
                candidates=candidates,
                provider_id=provider_id,
                model_name=model_name,
            )
            if payload.get("warning"):
                warnings.append(str(payload["warning"]))
            return ClassificationResult(
                assessments=assessments,
                warnings=warnings,
                classification_mode="llm",
                model_provider_id=provider_id,
                model_name=model_name,
                llm_used=True,
                deterministic_fallback_used=False,
            )
        except json.JSONDecodeError as exc:
            warning = f"LLM classification returned malformed JSON for provider {provider_id}: {exc.msg}"
            return ClassificationResult(
                assessments=[],
                warnings=[warning],
                model_error=warning,
                classification_mode="llm",
                model_provider_id=provider_id,
                model_name=model_name,
                llm_used=True,
                deterministic_fallback_used=False,
            )
        except (LLMClientError, TypeError, ValueError) as exc:
            warning = f"LLM classification failed for provider {provider_id}: {exc}"
            if self.config.fallback_to_deterministic:
                return self._deterministic_result(claim, candidates, context=context, fallback=True, warning=warning)
            return ClassificationResult(
                assessments=[],
                warnings=[warning],
                model_error=warning,
                classification_mode="llm",
                model_provider_id=provider_id,
                model_name=model_name,
                llm_used=True,
                deterministic_fallback_used=False,
            )


def classify_claim(
    claim: str,
    candidates: list[TaxonomyEntry] | list[object],
    *,
    context: str = "",
    provider_profile: ProviderProfile | None = None,
    fallback_to_deterministic: bool = True,
) -> ClassificationResult:
    mode: ClassificationMode = "llm" if provider_profile and provider_profile.provider_type != "deterministic" else "deterministic_baseline"
    classifier = ArgumentRiskClassifier(
        provider_profile=provider_profile,
        config=ClassifierConfig(mode=mode, fallback_to_deterministic=fallback_to_deterministic),
    )
    return classifier.classify_claim(claim, candidates, context=context)


def _coerce_llm_payload(raw: object) -> dict[str, Any]:
    if isinstance(raw, str):
        parsed = json.loads(raw)
    else:
        parsed = raw
    if not isinstance(parsed, dict):
        raise ValueError("LLM output must be a JSON object.")
    if "assessments" not in parsed:
        raise ValueError("LLM output missing assessments.")
    if not isinstance(parsed["assessments"], list):
        raise ValueError("LLM assessments must be a list.")
    return parsed


def _validate_llm_assessments(
    payload: dict[str, Any],
    *,
    claim: str,
    context: str,
    candidates: list[object],
    provider_id: str,
    model_name: str,
) -> tuple[list[RiskAssessment], list[str]]:
    entries = {_entry(candidate).id: _entry(candidate) for candidate in candidates if _is_entry_allowed(_entry(candidate))}
    haystack = claim if not context else f"{claim}\n{context}"
    assessments: list[RiskAssessment] = []
    warnings: list[str] = []

    for index, item in enumerate(payload.get("assessments", [])):
        if not isinstance(item, dict):
            warnings.append(f"Dropped LLM assessment {index}: item is not an object.")
            continue
        if item.get("insufficient_evidence") is True:
            continue
        risk_id = str(item.get("risk_id") or item.get("taxonomy_id") or "")
        entry = entries.get(risk_id)
        if entry is None:
            warnings.append(f"Dropped LLM assessment {index}: risk_id is not a supplied classification candidate.")
            continue
        evidence_span = str(item.get("evidence_span") or "")
        start = haystack.find(evidence_span) if evidence_span else -1
        if start < 0:
            warnings.append(f"Dropped LLM assessment {index}: evidence_span is not an exact substring.")
            continue
        confidence = _clamp_confidence(item.get("confidence", 0.0))
        if confidence <= 0:
            warnings.append(f"Dropped LLM assessment {index}: confidence must be positive.")
            continue
        assessments.append(
            RiskAssessment(
                risk_id=entry.id,
                category=entry.canonical_category,
                label=entry.name,
                severity=entry.severity.value,
                confidence=confidence,
                evidence_span=evidence_span,
                evidence_start_char=start,
                evidence_end_char=start + len(evidence_span),
                explanation=str(item.get("explanation") or "LLM classification grounded in supplied taxonomy candidate."),
                false_positive_warning=str(item.get("false_positive_warning") or ""),
                classification_mode="llm",
                model_provider_id=provider_id,
                model_name=model_name,
                llm_used=True,
                deterministic_fallback_used=False,
                insufficient_evidence=False,
            )
        )

    assessments.sort(key=lambda item: (-item.confidence, item.risk_id))
    return assessments[:3] if len(claim) <= 280 else assessments, warnings


def _entry(candidate: object) -> TaxonomyEntry:
    return getattr(candidate, "entry", candidate)


def _is_entry_allowed(entry: TaxonomyEntry) -> bool:
    return bool(entry.enabled_for_classification and entry.activation_status == "active")


def _clamp_confidence(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(min(1.0, max(0.0, number)), 3)
