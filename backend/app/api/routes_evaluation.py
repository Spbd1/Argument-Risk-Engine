from backend.app.services.evaluation_service import evaluate
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

@router.get("/run")
def run_evaluation() -> dict[str, object]:
    return evaluate()
