from backend.app.services.report_service import demo_report
from fastapi import APIRouter, Response

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/demo.md")
def report_demo() -> Response:
    return Response(content=demo_report(), media_type="text/markdown")
