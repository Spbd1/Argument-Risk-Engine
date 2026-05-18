from pydantic import BaseModel


class TaxonomyQualityResponse(BaseModel):
    errors: list[str]
    entry_count: int
