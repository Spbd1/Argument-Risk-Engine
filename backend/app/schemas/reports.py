from pydantic import BaseModel


class ReportResponse(BaseModel):
    content: str
