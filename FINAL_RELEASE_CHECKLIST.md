# Final Release Checklist

Do not mark an item DONE unless its verification command passes in the target release environment.

## Installation and local run

- [x] DONE — Editable install works.
  - verification command: `pip install -e .[dev]`
- [x] DONE — Python modules compile.
  - verification command: `python -m compileall backend engine tests uvicorn build_backend.py`
- [x] DONE — Unit/API tests pass.
  - verification command: `pytest`
- [x] DONE — Frontend dependencies install.
  - verification command: `cd frontend && npm install`
- [x] DONE — Frontend build completes.
  - verification command: `cd frontend && npm run build`
- [~] PARTIAL — One-command setup installs/seeds/starts, but long-running server command was intentionally time-limited in audit.
  - verification command: `python scripts/dev.py --install --run --open`

## Backend endpoints

- [x] DONE — `/health` responds.
  - verification command: `curl -fsS http://127.0.0.1:8002/health`
- [x] DONE — `/analyze` responds with deterministic analysis.
  - verification command: `curl -fsS -H 'Content-Type: application/json' -d '{"text":"The pilot program reduced wait times in one clinic."}' http://127.0.0.1:8002/analyze`
- [x] DONE — `/taxonomy` responds.
  - verification command: `curl -fsS http://127.0.0.1:8002/taxonomy`
- [x] DONE — `/taxonomy-workbench/coverage` responds.
  - verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage`
- [ ] NOT DONE — `/taxonomy-workbench/quality-report` responds but is not OK.
  - verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report | python -m json.tool`
- [x] DONE — `/settings/model-providers` responds without raw secrets.
  - verification command: `curl -fsS http://127.0.0.1:8002/settings/model-providers | python -m json.tool`
- [x] DONE — deterministic provider test works without API keys.
  - verification command: `curl -fsS -X POST http://127.0.0.1:8002/settings/model-providers/deterministic_baseline/test`
- [x] DONE — `/evaluation/run` responds.
  - verification command: `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run`
- [x] DONE — `/reports/from-analysis` generates JSON, Markdown, and HTML.
  - verification command: `POST /reports/from-analysis` with an analysis payload.

## Frontend

- [~] PARTIAL — Dashboard HTML and JS are served; Chrome interaction was not verified because Chrome is unavailable.
  - verification command: `curl -fsS http://127.0.0.1:5173` and `command -v google-chrome || command -v chromium || command -v chromium-browser`
- [ ] NOT DONE — Browser automation for Analyze, dropdowns, taxonomy browser, workbench import/export, settings, review, evaluation, and reports downloads.
  - verification command: future `npx playwright test`

## Taxonomy

- [x] DONE — Full-pack IDs are unique.
  - verification command: Python `Counter` check over `load_all_packs()`.
- [x] DONE — Workbook export works.
  - verification command: `python scripts/export_taxonomy_excel.py /tmp/are-taxonomy-audit.xlsx`
- [x] DONE — Workbook import works mechanically into a temporary root.
  - verification command: Python `import_workbook('/tmp/are-taxonomy-audit.xlsx', temp_root)`.
- [ ] NOT DONE — Active taxonomy quality gate passes.
  - verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report | python -m json.tool`
- [x] DONE — Healthy/deprecated/backlog exclusions pass code-level checks.
  - verification command: Python check over `load_all_packs()` and `active_classification_entries()`.
- [ ] NOT DONE — Full API-level regression coverage for healthy/deprecated/backlog exclusions.
  - verification command: future `pytest` tests covering imported full taxonomy.

## Retrieval/classification/scoring

- [x] DONE — Neutral text smoke check returns no aggressive starter-pack labels.
  - verification command: Python `analyze_text('The meeting starts at 10 AM...')`.
- [x] DONE — LLM invented taxonomy labels are dropped in `ArgumentRiskClassifier` unit smoke.
  - verification command: Python fake LLM classifier smoke.
- [x] DONE — LLM failure is visible in `ArgumentRiskClassifier` warnings.
  - verification command: Python fake `LLMClientError` smoke.
- [ ] NOT DONE — Analyze endpoint actually uses selected LLM providers.
  - verification command: inspect `engine/argument_risk_engine/analyzer.py` and run `/analyze` with `mode: llm`.
- [ ] NOT DONE — False-positive rate is release-ready.
  - verification command: `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run | python -m json.tool`

## Reports and documentation

- [x] DONE — Markdown report includes limitations note.
  - verification command: Python `render_markdown_report(...)`.
- [x] DONE — HTML report includes limitations note.
  - verification command: Python `render_html_report(...)`.
- [x] DONE — JSON report includes limitations note.
  - verification command: Python `render_json_report(...)`.
- [x] DONE — README and limitations docs avoid claims of scientific validation or truth/intent judgment.
  - verification command: inspect `README.md` and `docs/limitations.md`.
