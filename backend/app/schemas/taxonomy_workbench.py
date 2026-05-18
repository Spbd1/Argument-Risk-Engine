from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyEntry

from pydantic import BaseModel, Field


class TaxonomyPackSummary(BaseModel):
    pack: str
    entry_count: int
    active_count: int
    enabled_for_classification_count: int


class TaxonomyPacksResponse(BaseModel):
    packs: list[TaxonomyPackSummary]


class TaxonomyCoverageResponse(BaseModel):
    entry_count: int
    active_count: int
    enabled_for_classification_count: int
    review_required_count: int = 0
    deprecated_count: int = 0
    by_category: dict[str, int] = Field(default_factory=dict)
    by_pack: dict[str, int] = Field(default_factory=dict)
    by_detection_level: dict[str, int] = Field(default_factory=dict)
    by_academic_status: dict[str, int] = Field(default_factory=dict)
    by_activation_status: dict[str, int] = Field(default_factory=dict)
    missing_examples_count: int = 0
    missing_false_positive_warnings_count: int = 0


class TaxonomyQualityResponse(BaseModel):
    ok: bool
    entry_count: int
    active_classification_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    coverage: dict[str, object] = Field(default_factory=dict)


class TaxonomyImportResult(BaseModel):
    entry_count: int
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    backup_paths: list[str] = Field(default_factory=list)


class TaxonomyValidationResponse(BaseModel):
    ok: bool
    entry_count: int
    active_classification_count: int = 0
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)


class ActivationRequest(BaseModel):
    activation_status: str = "active"
    enabled_for_classification: bool | None = None


class ActivationResponse(BaseModel):
    entry: TaxonomyEntry
    backup_path: str
