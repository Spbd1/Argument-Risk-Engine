from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    items: int
