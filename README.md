# Argument-Risk-Engine

Argument-Risk-Engine is a local-first, taxonomy-grounded web application for reviewing argument-level risk patterns in text. It combines a FastAPI backend, a React dashboard, file-based taxonomy packs, evidence-span extraction, reports, and a small evaluation harness so contributors can install it quickly, inspect outputs, and improve the taxonomy without needing a database.

**The goal is not to automate moral judgement or determine truth. The system identifies argument-level risk patterns and provides evidence-grounded explanations for human review.**

## What the system does

- Splits submitted text into reviewable claims.
- Retrieves active taxonomy entries that match each claim.
- Produces conservative risk findings only when textual evidence is available.
- Shows evidence spans, confidence, severity, explanations, and false-positive warnings.
- Lets users import/export taxonomy Excel workbooks from Chrome or the CLI.
- Lets users configure deterministic or external model-provider profiles from Chrome.
- Generates downloadable Markdown, HTML, and JSON reports.
- Runs a small benchmark set with positives, negatives, and hard negatives for regression checks.

## What the system does not do

- It does **not** automate moderation, enforcement, ranking, or eligibility decisions.
- It does **not** determine whether a statement is factually true.
- It does **not** infer author intent or diagnose a person’s beliefs, bias, or character.
- It does **not** replace trained human review in high-stakes workflows.
- It does **not** claim that the current taxonomy is complete or scientifically validated.

## Architecture

```text
Chrome dashboard (React/Vite)
  |-- Analyze text / save report
  |-- Taxonomy workbench import/export
  |-- Model settings
  |-- Evaluation and review pages
          |
          v
FastAPI backend (backend/app)
  |-- /api/analyze
  |-- /api/taxonomy-workbench/*
  |-- /api/settings/*
  |-- /api/reports/*
          |
          v
Argument risk engine (engine/argument_risk_engine)
  |-- claim extraction
  |-- lexical retrieval over active taxonomy packs
  |-- deterministic baseline classifier
  |-- scoring, calibration, explanation, reports
          |
          v
Local files only for MVP (data/)
  |-- taxonomy packs and workbook imports/exports
  |-- model profile YAML
  |-- demo inputs and benchmark JSONL
  |-- review queue and generated reports
```

## One-command setup

From the repository root:

```bash
python scripts/dev.py --install --run --open
```

This command will:

1. Create or reuse `.venv`.
2. Install backend dependencies with `pip install -e .[dev]`.
3. Install frontend dependencies with `npm install` in `frontend/`.
4. Seed demo data and benchmark files.
5. Import the first `.xlsx` workbook found in `data/taxonomy/imports/` if one is available.
6. Start the backend at <http://localhost:8000>.
7. Start the frontend at <http://localhost:5173>.
8. Open the dashboard in your default browser.

Stop both servers with `Ctrl+C`.

## Manual backend setup

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python scripts/seed_demo_data.py
python scripts/run_backend.py
```

Backend health check:

```bash
curl http://localhost:8000/health
```

## Manual frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open <http://localhost:5173> in Chrome. The Vite app calls the backend at `http://localhost:8000` by default.

## Docker setup

```bash
docker compose up --build
```

The compose file starts:

- `backend`: FastAPI service on <http://localhost:8000>.
- `frontend`: Vite dashboard on <http://localhost:5173>.
- `are-data`: a named volume mounted at `/app/data` for MVP file storage.

No database is required for the MVP.

## Dashboard guide

1. Open <http://localhost:5173> in Chrome.
2. Use **Analyze** to paste text, run analysis, inspect claim cards, and save a report.
3. Use **Reports** to preview and download saved reports.
4. Use **Taxonomy Workbench** to validate packs, import an `.xlsx` workbook, export an `.xlsx` workbook, inspect coverage, and activate/deactivate entries.
5. Use **Model Settings** to select the deterministic baseline or configure an OpenAI-compatible provider profile.
6. Use **Evaluation** to run the bundled mini benchmark and inspect error categories.
7. Use **Review** to inspect persisted review items and feedback examples.

See `docs/dashboard_user_guide.md` for a screen-by-screen walkthrough.

## Taxonomy import/export guide

### From Chrome

1. Open **Taxonomy Workbench**.
2. Choose a user-managed `.xlsx` workbook.
3. Click **Import Excel**.
4. Review import errors/warnings.
5. Click **Validate taxonomy**.
6. Click **Export Excel** to download the current active taxonomy workbook.

### From the CLI

```bash
python scripts/import_taxonomy_excel.py --input data/taxonomy/imports/argument_risk_taxonomy_living_workbook_v2_taxonomy_first.xlsx
python scripts/export_taxonomy_excel.py data/taxonomy/exports/taxonomy.xlsx
```

The real taxonomy workbook is intentionally not committed. Generated import/export artifacts should remain local.

## Model provider configuration

The deterministic local baseline is the default and requires no API key. Provider metadata is stored in `data/config/model_profiles.yaml`; the active provider is stored in `data/config/app_settings.yaml`. Secrets should be supplied through environment variables or a local `.env` file copied from `.env.example`.

```bash
cp .env.example .env
# edit ARE_LLM_PROVIDER, ARE_OPENAI_API_KEY, or custom provider values as needed
```

External providers are optional. When using them, keep output conservative and evidence-grounded; do not treat model output as a truth oracle.

## API examples

Analyze text:

```bash
curl -s http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Everyone on the project always ignores the checklist, even though the last review found exceptions."}'
```

List taxonomy entries:

```bash
curl -s http://localhost:8000/api/taxonomy
```

Export taxonomy workbook:

```bash
curl -L http://localhost:8000/api/taxonomy-workbench/export-excel -o taxonomy.xlsx
```

Generate a report from an analysis payload through the dashboard or:

```bash
curl -s http://localhost:8000/api/reports
```

## Example JSON output

```json
{
  "analysis_id": "analysis_...",
  "summary": {
    "risk_count": 1,
    "highest_severity": "medium",
    "requires_human_review": true
  },
  "claims": [
    {
      "claim_id": "claim_1",
      "text": "Everyone on the project always ignores the checklist",
      "risks": [
        {
          "risk_id": "overgeneralization",
          "label": "Overgeneralization",
          "severity": "medium",
          "confidence": 0.72,
          "evidence_span": "Everyone",
          "explanation": "The claim uses broad quantifier language and should be reviewed for overreach."
        }
      ]
    }
  ],
  "warnings": ["Human review is required before using this output in consequential settings."]
}
```

Exact field order and confidence values may differ as the taxonomy and scoring rules evolve.

## Evaluation notes

Run:

```bash
make evaluate
```

The mini benchmark in `data/benchmarks/mini_eval_set.jsonl` is a practical regression set, not a scientific validation set. It includes positives, negatives, and hard negatives to monitor over-classification. Treat metrics as engineering signals and review false positives/false negatives manually.

## Limitations

The system may produce false positives, miss subtle risks, and should not be used for automated moderation. It does not judge intent, determine factual truth, or diagnose bias in a person. Human review is required for high-stakes use. A large taxonomy does not mean a complete taxonomy, and it does not mean aggressive classification. See `docs/limitations.md`.

## Roadmap

Near-term priorities are stronger taxonomy quality checks, richer benchmark coverage, better report templates, provider-specific testing, and packaging improvements. See `docs/roadmap.md`.

## Contributing

- Keep claims conservative and evidence-grounded.
- Add tests for engine, API, and import/export changes.
- Update docs when changing routes, setup, taxonomy schema, or dashboard behavior.
- Do not commit private taxonomy workbooks, API keys, generated reports, or local review artifacts.
- Run `make test` and `make evaluate` before opening a pull request.
