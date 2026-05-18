from typing import Any

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1)

class AnalysisResponse(BaseModel):
    analysis_id: str
    summary: dict[str, Any]
    claims: list[dict[str, Any]]
    risks: list[dict[str, Any]]
