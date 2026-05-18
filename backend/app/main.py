from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api import (
    routes_analysis,
    routes_evaluation,
    routes_reports,
    routes_review,
    routes_settings,
    routes_taxonomy,
    routes_taxonomy_workbench,
)
from backend.app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="Argument-Risk-Engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_analysis.router)
app.include_router(routes_taxonomy.router)
app.include_router(routes_taxonomy_workbench.router)
app.include_router(routes_review.router)
app.include_router(routes_evaluation.router)
app.include_router(routes_settings.router)
app.include_router(routes_reports.router)
app.include_router(routes_analysis.router, prefix="/api")
app.include_router(routes_taxonomy.router, prefix="/api")
app.include_router(routes_taxonomy_workbench.router, prefix="/api")
app.include_router(routes_review.router, prefix="/api")
app.include_router(routes_evaluation.router, prefix="/api")
app.include_router(routes_settings.router, prefix="/api")
app.include_router(routes_reports.router, prefix="/api")

@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
