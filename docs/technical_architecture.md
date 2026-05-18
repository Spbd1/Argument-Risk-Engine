# Technical Architecture

Argument-Risk-Engine is an MVP local web application composed of a React dashboard, a FastAPI backend, an argument-risk engine package, and file-based data storage. The design favors transparency, reproducibility, and easy contribution over production-scale infrastructure.

## System boundaries

```text
User in Chrome
  -> React dashboard (frontend/)
  -> FastAPI API (backend/app/)
  -> Engine package (engine/argument_risk_engine/)
  -> Local data files (data/)
```

There is no database requirement for the MVP. Runtime state is persisted as YAML, JSON, JSONL, Markdown, HTML, and Excel files under `data/`.

## Components

### Frontend

- Location: `frontend/`
- Framework: React + Vite + TypeScript
- Responsibilities:
  - Text analysis UI
  - Evidence and risk cards
  - Taxonomy workbench import/export controls
  - Model provider settings
  - Evaluation and review views
  - Report preview/download UX

### Backend

- Location: `backend/app/`
- Framework: FastAPI
- Responsibilities:
  - API routing
  - Request/response schemas
  - Service adapters around the engine package
  - File-backed settings, review, taxonomy, report, and evaluation workflows

### Engine

- Location: `engine/argument_risk_engine/`
- Responsibilities:
  - Claim extraction
  - Taxonomy loading and validation
  - Lexical candidate retrieval
  - Deterministic baseline classification
  - Risk scoring and calibration
  - Evidence-grounded explanations
  - Evaluation metrics
  - Report rendering

### Data layout

```text
data/
  benchmarks/       Mini JSONL evaluation sets
  config/           File-backed app and provider settings
  examples/         Demo input JSONL
  reports/          Generated local report artifacts
  review/           Review queue JSONL
  taxonomy/         YAML packs, workbook imports, exports, source metadata
```

## Request flow

1. The user submits text in Chrome.
2. The dashboard calls `POST /api/analyze`.
3. The backend validates the request and calls the analyzer service.
4. The engine extracts claims.
5. Each claim retrieves candidate taxonomy entries.
6. The deterministic baseline emits findings only when evidence spans are present.
7. Scoring assigns confidence and severity.
8. The backend returns claims, risks, evidence spans, warnings, and summary metadata.
9. The dashboard renders results and can save a report.

## Taxonomy flow

- YAML packs are loaded from `data/taxonomy/packs/`.
- Excel imports are parsed, validated, and converted to pack YAML.
- Excel exports serialize the current local taxonomy into a workbook.
- Activation flags determine whether entries are retrievable and classifiable.
- Human review is required before using taxonomy changes in consequential settings.

## Model provider flow

The deterministic baseline is the default. Optional provider profiles can be configured through the dashboard or YAML files. Secrets should be provided through local environment variables, not committed files. Provider outputs must remain evidence-grounded and should be treated as review assistance rather than truth determination.

## Deployment model

The practical open-source target is local development:

- `python scripts/dev.py --install --run --open` for one-command local startup.
- `docker compose up --build` for containerized startup.
- `make test` for local checks.
- `make evaluate` for mini benchmark regression checks.

## Non-goals for the MVP

- Multi-user authentication
- Central database
- Automated moderation
- Automated truth determination
- Production observability stack
- Scientific validation claims
