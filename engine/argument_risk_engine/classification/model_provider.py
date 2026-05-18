from pydantic import BaseModel


class ModelProvider(BaseModel):
    name: str = "deterministic"
    model: str = "local-keyword"
    temperature: float = 0.0
