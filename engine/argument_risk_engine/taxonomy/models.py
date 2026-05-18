from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaxonomyEntry(BaseModel):
    id: str
    name: str
    description: str
    severity: RiskSeverity = RiskSeverity.low
    keywords: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    mitigation: str = "Escalate for human review."
    active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "description")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be non-empty")
        return value.strip()

    @field_validator("keywords", "examples")
    @classmethod
    def clean_strings(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item and item.strip()]


class TaxonomyPack(BaseModel):
    version: str = "0.1.0"
    name: str = "default"
    entries: list[TaxonomyEntry] = Field(default_factory=list)


def default_taxonomy_pack() -> TaxonomyPack:
    return TaxonomyPack(
        name="starter-pack",
        entries=[
            TaxonomyEntry(
                id="overgeneralization",
                name="Overgeneralization",
                description="A broad claim that applies a judgement to a group or situation without sufficient qualification.",
                severity=RiskSeverity.medium,
                keywords=["always", "never", "everyone", "all", "none"],
                examples=["Everyone in that group is dishonest."],
                mitigation="Ask for scope, counterexamples, and supporting evidence.",
            ),
            TaxonomyEntry(
                id="unsupported_causal_claim",
                name="Unsupported causal claim",
                description="A statement presents causation without evidence in the provided text.",
                severity=RiskSeverity.medium,
                keywords=["caused", "because of", "leads to", "responsible for"],
                examples=["The policy caused every later problem."],
                mitigation="Request causal evidence and consider alternative explanations.",
            ),
            TaxonomyEntry(
                id="dehumanizing_language",
                name="Dehumanizing language",
                description="Language that depicts people as less than human or as pests, disease, or objects.",
                severity=RiskSeverity.high,
                keywords=["vermin", "parasites", "infestation", "animals"],
                examples=["They are vermin."],
                mitigation="Escalate for careful human review and contextual assessment.",
            ),
        ],
    )
