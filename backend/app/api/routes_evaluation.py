from __future__ import annotations

from backend.app.schemas.evaluation import EvaluationRunRequest
from backend.app.services.evaluation_service import evaluate, evaluation_errors, evaluation_summary
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/run")
def run_evaluation(payload: EvaluationRunRequest) -> dict[str, object]:
    return evaluate(payload.benchmark_path)


@router.get("/run")
def run_evaluation_legacy() -> dict[str, object]:
    return evaluate()


@router.get("/summary")
def summary() -> dict[str, object]:
    return evaluation_summary()


@router.get("/errors")
def errors() -> dict[str, object]:
    return evaluation_errors()
