from __future__ import annotations

from argument_risk_engine.taxonomy.models import TaxonomyEntry

from pydantic import BaseModel, Field


class TaxonomyListResponse(BaseModel):
    entries: list[TaxonomyEntry]
    total: int = 0


class TaxonomyEntryResponse(BaseModel):
    entry: TaxonomyEntry


class TaxonomyCategoriesResponse(BaseModel):
    categories: list[str]


class TaxonomySummaryResponse(BaseModel):
    entry_count: int
    active_count: int
    enabled_for_classification_count: int
    by_category: dict[str, int] = Field(default_factory=dict)
    by_pack: dict[str, int] = Field(default_factory=dict)
    by_activation_status: dict[str, int] = Field(default_factory=dict)


class TaxonomySearchResponse(BaseModel):
    entries: list[TaxonomyEntry]
    query: str
    total: int = 0
