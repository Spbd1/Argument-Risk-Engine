from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CanonicalCategory(str, Enum):
    fallacy = "fallacy"
    cognitive_bias = "cognitive_bias"
    behavioural_bias = "behavioural_bias"
    evidence_failure = "evidence_failure"
    uncertainty_failure = "uncertainty_failure"
    causal_reasoning_error = "causal_reasoning_error"
    statistical_reasoning_error = "statistical_reasoning_error"
    rhetorical_pattern = "rhetorical_pattern"
    social_influence_pattern = "social_influence_pattern"
    manipulation_pattern = "manipulation_pattern"
    healthy_reasoning_pattern = "healthy_reasoning_pattern"
    operational_detection_category = "operational_detection_category"


class AcademicStatus(str, Enum):
    canonical = "canonical"
    recognized_subtype = "recognized_subtype"
    debated = "debated"
    operational = "operational"
    deprecated = "deprecated"


class AcademicConsensus(str, Enum):
    high = "high"
    medium = "medium"
    debated = "debated"
    operational_only = "operational_only"


class DetectionLevel(str, Enum):
    lexical = "lexical"
    structural = "structural"
    contextual = "contextual"
    discourse = "discourse"
    cross_claim = "cross_claim"


class ActivationStatus(str, Enum):
    active = "active"
    review_required = "review_required"
    backlog = "backlog"
    deprecated = "deprecated"


class FalsePositiveSensitivity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


_LIST_FIELDS = {
    "signals",
    "trigger_patterns",
    "exclusion_criteria",
    "common_false_positives",
    "positive_examples",
    "negative_examples",
    "severity_guidance",
    "related_risks",
    "synonym_ids",
    "source_refs",
}


def normalize_id(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def split_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in re.split(r"[;\n]+", str(value)) if part.strip()]


def parse_bool(value: object, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1", "enabled", "active"}:
        return True
    if text in {"no", "n", "false", "0", "disabled", "inactive", "n/a", "na"}:
        return False
    return default


def _enum_value(enum: type[Enum], value: object, default: str) -> str:
    normalized = normalize_id(value) if value not in {None, ""} else default
    return normalized if normalized in {item.value for item in enum} else default


class TaxonomyEntry(BaseModel):
    id: str
    name: str
    pack: str = "core_mvp"
    canonical_category: str = CanonicalCategory.operational_detection_category.value
    academic_status: str = AcademicStatus.operational.value
    academic_consensus: str = AcademicConsensus.operational_only.value
    short_definition: str = ""
    long_definition: str = ""
    detection_level: str = DetectionLevel.contextual.value
    signals: list[str] = Field(default_factory=list)
    trigger_patterns: list[str] = Field(default_factory=list)
    minimum_evidence_requirement: str = ""
    exclusion_criteria: list[str] = Field(default_factory=list)
    common_false_positives: list[str] = Field(default_factory=list)
    positive_examples: list[str] = Field(default_factory=list)
    negative_examples: list[str] = Field(default_factory=list)
    severity_guidance: list[str] = Field(default_factory=list)
    related_risks: list[str] = Field(default_factory=list)
    synonym_ids: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    enabled_for_mvp: bool = False
    enabled_for_retrieval: bool = False
    enabled_for_classification: bool = False
    requires_context: bool = False
    requires_human_judgment: bool = False
    false_positive_sensitivity: str = FalsePositiveSensitivity.medium.value
    activation_status: str = ActivationStatus.review_required.value
    healthy_suppressor: bool = False
    model_assisted_allowed: bool = True
    notes: str = ""
    row_number: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        # Backwards-compatible aliases used by the original starter taxonomy/tests.
        if "description" in data and "short_definition" not in data:
            data["short_definition"] = data["description"]
        if "keywords" in data and "signals" not in data:
            data["signals"] = data["keywords"]
        if "examples" in data and "positive_examples" not in data:
            data["positive_examples"] = data["examples"]
        if "active" in data and "enabled_for_classification" not in data:
            data["enabled_for_classification"] = parse_bool(data["active"])
            data.setdefault("activation_status", ActivationStatus.active.value if data["enabled_for_classification"] else ActivationStatus.review_required.value)
        data["id"] = normalize_id(data.get("id"))
        data["pack"] = normalize_id(data.get("pack") or "core_mvp")
        invalid_enums: dict[str, str] = {}
        enum_specs = {
            "canonical_category": (CanonicalCategory, CanonicalCategory.operational_detection_category.value),
            "academic_status": (AcademicStatus, AcademicStatus.operational.value),
            "academic_consensus": (AcademicConsensus, AcademicConsensus.operational_only.value),
            "detection_level": (DetectionLevel, DetectionLevel.contextual.value),
            "activation_status": (ActivationStatus, ActivationStatus.review_required.value),
            "false_positive_sensitivity": (FalsePositiveSensitivity, FalsePositiveSensitivity.medium.value),
        }
        for field_name, (enum_type, default) in enum_specs.items():
            raw_value = data.get(field_name)
            normalized = normalize_id(raw_value) if raw_value not in {None, ""} else default
            allowed = {item.value for item in enum_type}
            if normalized not in allowed:
                invalid_enums[field_name] = str(raw_value)
                normalized = default
            data[field_name] = normalized
        metadata = dict(data.get("metadata") or {})
        if invalid_enums:
            metadata["invalid_enums"] = invalid_enums
        data["metadata"] = metadata
        for field in _LIST_FIELDS:
            data[field] = split_list(data.get(field))
        for field in ["enabled_for_mvp", "enabled_for_retrieval", "enabled_for_classification", "requires_context", "requires_human_judgment", "healthy_suppressor", "model_assisted_allowed"]:
            data[field] = parse_bool(data.get(field), default=(field == "model_assisted_allowed"))
        super().__init__(**data)
        if not self.id:
            raise ValueError("id must be non-empty")
        if not str(self.name or "").strip():
            raise ValueError("name must be non-empty")

    @property
    def description(self) -> str:
        return self.short_definition or self.long_definition

    @property
    def keywords(self) -> list[str]:
        return self.signals + self.trigger_patterns

    @property
    def examples(self) -> list[str]:
        return self.positive_examples

    @property
    def active(self) -> bool:
        return self.enabled_for_classification and self.activation_status == ActivationStatus.active.value

    @property
    def severity(self) -> RiskSeverity:
        if any("high" in item.lower() for item in self.severity_guidance):
            return RiskSeverity.high
        if any("medium" in item.lower() for item in self.severity_guidance):
            return RiskSeverity.medium
        return RiskSeverity.low

    @property
    def mitigation(self) -> str:
        return "Escalate for human review." if self.requires_human_judgment else "Require clear textual evidence and review false-positive guards."


class TaxonomyPack(BaseModel):
    version: str = "0.1.0"
    name: str = "default"
    entries: list[TaxonomyEntry] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def default_taxonomy_pack() -> TaxonomyPack:
    return TaxonomyPack(
        name="starter-pack",
        entries=[
            TaxonomyEntry(
                id="overgeneralization",
                name="Overgeneralization",
                pack="starter_pack",
                canonical_category="fallacy",
                academic_status="canonical",
                academic_consensus="high",
                short_definition="A broad claim that applies a judgement without sufficient qualification.",
                detection_level="structural",
                signals=["always", "never", "everyone", "all", "none"],
                positive_examples=["Everyone in that group is dishonest."],
                negative_examples=["Every backup completed successfully according to the job log."],
                minimum_evidence_requirement="Evidence span showing an overbroad quantifier applied as support.",
                common_false_positives=["Legitimate quantified claims with adequate evidence."],
                enabled_for_mvp=True,
                enabled_for_retrieval=True,
                enabled_for_classification=True,
                activation_status="active",
                severity_guidance=["medium"],
                source_refs=["starter"],
            ),
            TaxonomyEntry(
                id="dehumanizing_language",
                name="Dehumanizing language",
                pack="starter_pack",
                canonical_category="rhetorical_pattern",
                academic_status="operational",
                academic_consensus="operational_only",
                short_definition="Language that depicts people as less than human or as pests, disease, or objects.",
                detection_level="lexical",
                signals=["vermin", "parasites", "infestation", "animals"],
                positive_examples=["They are vermin."],
                negative_examples=["The novel describes animals in a literal zoo."],
                minimum_evidence_requirement="A quoted span applying dehumanizing terms to people or groups.",
                common_false_positives=["Literal uses about non-human animals or pests."],
                enabled_for_mvp=True,
                enabled_for_retrieval=True,
                enabled_for_classification=True,
                activation_status="active",
                severity_guidance=["high"],
                requires_human_judgment=True,
                source_refs=["starter"],
            ),
        ],
    )
