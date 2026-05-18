from argument_risk_engine.taxonomy.models import TaxonomyEntry

from pydantic import BaseModel


class TaxonomyListResponse(BaseModel):
    entries: list[TaxonomyEntry]
