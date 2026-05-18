from pydantic import BaseModel


class ReviewFeedback(BaseModel):
    analysis_id: str
    taxonomy_id: str | None = None
    decision: str
    notes: str = ""
