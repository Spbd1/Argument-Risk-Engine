from argument_risk_engine.classification.classifier import ArgumentRiskClassifier, ClassifierConfig
from argument_risk_engine.classification.deterministic import classify_deterministic
from argument_risk_engine.classification.llm_client import LLMClientError
from argument_risk_engine.classification.model_provider import ProviderProfile
from argument_risk_engine.taxonomy.models import TaxonomyEntry, default_taxonomy_pack


def _entry(**overrides):
    data = {
        "id": "risk",
        "name": "Risk",
        "canonical_category": "fallacy",
        "signals": ["always"],
        "enabled_for_classification": True,
        "activation_status": "active",
        "severity_guidance": ["medium"],
    }
    data.update(overrides)
    return TaxonomyEntry(**data)


class FakeLLMClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def classify(self, prompt, *, messages=None):
        self.calls.append((prompt, messages))
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def test_classifier_returns_match():
    entry = default_taxonomy_pack().entries[0]
    assert classify_deterministic("everyone always", [entry])[0]["taxonomy_id"] == entry.id


def test_deterministic_baseline_works_without_api_key_and_validates_evidence():
    entry = _entry(id="overgeneralization", name="Overgeneralization", signals=["always"])

    result = ArgumentRiskClassifier().classify_claim("People always do this.", [entry])

    assert result.assessments[0].risk_id == "overgeneralization"
    assert result.assessments[0].evidence_span == "always"
    assert result.assessments[0].llm_used is False
    assert result.assessments[0].model_provider_id == "deterministic_baseline"


def test_deterministic_ignores_inactive_excluded_and_neutral_claims():
    inactive = _entry(id="inactive", activation_status="review_required")
    excluded = _entry(id="excluded", exclusion_criteria=["legitimate quantified claims"])

    assert classify_deterministic("People always do this.", [inactive]) == []
    assert classify_deterministic("This is about legitimate quantified claims and always includes evidence.", [excluded]) == []
    assert classify_deterministic("The meeting starts at noon.", [_entry()]) == []


def test_llm_mode_uses_selected_provider_and_rejects_invented_labels():
    profile = ProviderProfile(
        provider_id="selected_provider",
        label="Selected Provider",
        provider_type="openai_compatible",
        base_url="http://example.test/v1",
        model_name="selected-model",
        enabled=True,
    )
    entry = _entry(id="allowed", name="Allowed", signals=["always"])
    llm = FakeLLMClient(
        {
            "assessments": [
                {"risk_id": "invented", "confidence": 0.99, "evidence_span": "always"},
                {"risk_id": "allowed", "confidence": 0.71, "evidence_span": "always", "explanation": "Exact evidence."},
            ]
        }
    )

    result = ArgumentRiskClassifier(provider_profile=profile, llm_client=llm).classify_claim("People always do this.", [entry])

    assert len(result.assessments) == 1
    assert result.assessments[0].risk_id == "allowed"
    assert result.assessments[0].model_provider_id == "selected_provider"
    assert result.assessments[0].model_name == "selected-model"
    assert result.assessments[0].llm_used is True
    assert result.warnings
    assert llm.calls


def test_llm_evidence_spans_are_validated():
    profile = ProviderProfile(
        provider_id="selected_provider",
        label="Selected Provider",
        provider_type="openai_compatible",
        base_url="http://example.test/v1",
        model_name="selected-model",
        enabled=True,
    )
    entry = _entry(id="allowed", name="Allowed", signals=["always"])
    llm = FakeLLMClient({"assessments": [{"risk_id": "allowed", "confidence": 0.8, "evidence_span": "not in claim"}]})

    result = ArgumentRiskClassifier(provider_profile=profile, llm_client=llm).classify_claim("People always do this.", [entry])

    assert result.assessments == []
    assert any("evidence_span" in warning for warning in result.warnings)


def test_llm_provider_failure_falls_back_without_crashing():
    profile = ProviderProfile(
        provider_id="selected_provider",
        label="Selected Provider",
        provider_type="openai_compatible",
        base_url="http://example.test/v1",
        model_name="selected-model",
        enabled=True,
    )
    entry = _entry(id="allowed", name="Allowed", signals=["always"])
    llm = FakeLLMClient(LLMClientError("provider unavailable"))

    result = ArgumentRiskClassifier(provider_profile=profile, llm_client=llm).classify_claim("People always do this.", [entry])

    assert result.assessments[0].risk_id == "allowed"
    assert result.deterministic_fallback_used is True
    assert result.assessments[0].deterministic_fallback_used is True
    assert result.model_error


def test_llm_malformed_output_returns_empty_warning_without_crashing():
    profile = ProviderProfile(
        provider_id="selected_provider",
        label="Selected Provider",
        provider_type="openai_compatible",
        base_url="http://example.test/v1",
        model_name="selected-model",
        enabled=True,
    )
    classifier = ArgumentRiskClassifier(
        provider_profile=profile,
        llm_client=FakeLLMClient("not json"),
        config=ClassifierConfig(mode="llm", fallback_to_deterministic=True),
    )

    result = classifier.classify_claim("People always do this.", [_entry(id="allowed")])

    assert result.assessments == []
    assert result.warnings
    assert "malformed JSON" in result.model_error
    assert result.deterministic_fallback_used is False
