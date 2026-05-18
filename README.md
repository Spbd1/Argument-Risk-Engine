# Argument-Risk-Engine

Argument-Risk-Engine is a practical, local, Chrome-first web application for taxonomy-grounded argument risk analysis. It is designed for human review: it does **not** automate moral judgement or decide truth. It identifies argument-level risk patterns and explains them with evidence grounded in the submitted text and active taxonomy.

## Core principles

- **Taxonomy-first:** every risk label comes from an explicit taxonomy entry.
- **Evidence-grounded:** reports quote or locate supporting text spans.
- **Conservative:** uncertain findings are marked as low confidence or omitted.
- **Local-first:** the MVP runs without authentication or a database.
- **Configurable models:** deterministic local analysis is the default; paid LLM providers can be configured through `data/config/model_profiles.yaml`.
- **Workbook friendly:** taxonomy packs can be imported from and exported to Excel workbooks. The real taxonomy workbook is a user-managed external file and is intentionally not committed to Git.

## One-command setup

From the repository root, run:

```bash
python scripts/dev.py --install --run --open
```

The command creates or reuses `.venv`, installs Python dependencies, installs frontend dependencies, seeds demo data, starts the FastAPI backend at <http://localhost:8000>, starts the Vite dashboard at <http://localhost:5173>, and opens the dashboard in your default browser.

## Manual setup

```bash
make install
make test
make run-backend
make run-frontend
```

Useful commands:

```bash
make dev              # install, seed, run, and open the dashboard
make evaluate         # run the bundled mini evaluation set
make import-taxonomy  # import an Excel taxonomy workbook
make export-taxonomy  # export the active taxonomy to Excel
```

## Taxonomy workbook imports

The real taxonomy workbook should be imported later from the dashboard or CLI and is intentionally not committed to Git. Place a local copy under `data/taxonomy/imports/` or choose it from Chrome in the Taxonomy Workbench. For CLI imports, run:

```bash
python scripts/import_taxonomy_excel.py --input data/taxonomy/imports/argument_risk_taxonomy_living_workbook_v2_taxonomy_first.xlsx
```

Generated Excel exports and report files are local artifacts and are ignored by Git. Empty import/export/report directories are kept with `.gitkeep` files.

## API overview

- `POST /api/analysis/analyze` analyzes text and returns claims, risks, evidence, and a conservative summary.
- `GET /api/taxonomy` lists active taxonomy entries.
- `POST /api/taxonomy-workbench/import` imports an Excel workbook.
- `GET /api/taxonomy-workbench/export` exports the taxonomy workbook.
- `GET /api/settings` and `PUT /api/settings` manage local model settings.
- `GET /api/reports/{analysis_id}.md` returns a markdown report.

## Development notes

The MVP intentionally uses plain files under `data/` instead of a database. Review feedback is appended to `data/review/review_store.jsonl`; taxonomy packs live under `data/taxonomy/packs`; reports are written to `data/reports`.

See `docs/technical_architecture.md`, `docs/taxonomy_design.md`, and `docs/dashboard_user_guide.md` for details.
