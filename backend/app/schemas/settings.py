from pydantic import BaseModel


class AppSettings(BaseModel):
    llm_provider: str = "deterministic"
    model: str = "local-keyword"
    temperature: float = 0.0
