# Argument-Risk-Engine Production Audit Report

Audit date: 2026-05-18 UTC

## Executive summary

The repository now passes the automated compile, unit/API, frontend install/build, HTTP smoke, taxonomy workbook export/import, and deterministic analysis smoke checks listed below. During the audit I fixed three local-run blockers rather than leaving them as documentation-only findings:

1. `uvicorn backend.app.main:app --reload` did not resolve to a runnable console script after `pip install -e .[dev]`.
2. The bundled `uvicorn` shim only answered `/health` and did not dispatch application routes over HTTP.
3. The requested non-`/api` taxonomy/workbench/settings endpoints were not mounted.

Remaining release risks are mostly quality and usability issues: the dashboard/API still use the small starter pack as the active taxonomy, the starter pack quality report fails, the mini benchmark shows a high false-positive rate, and the analysis service does not actually execute an LLM provider path when a non-deterministic provider is selected.

## Verification performed

| Area | Command / check | Result |
| --- | --- | --- |
| Install | `pip install -e .[dev]` | PASS |
| Compile | `python -m compileall backend engine tests uvicorn build_backend.py` | PASS |
| Tests | `pytest` | PASS: 42 passed, 4 collection warnings from the local FastAPI test-client shim |
| Frontend install | `cd frontend && npm install` | PASS, with npm `http-proxy` environment warning |
| Frontend build | `cd frontend && npm run build` | PASS |
| One-command setup | `timeout 12s python scripts/dev.py --install --run --open` | WARNING: install/seed/frontend startup completed, then timed out intentionally because dev servers are long-running |
| Backend server | `uvicorn backend.app.main:app --reload --port 8002` | PASS after fix |
| Health | `curl -fsS http://127.0.0.1:8002/health` | PASS |
| Analyze | `curl -fsS -H 'Content-Type: application/json' -d '{...}' http://127.0.0.1:8002/analyze` | PASS |
| Taxonomy | `curl -fsS http://127.0.0.1:8002/taxonomy` | PASS after root-route fix |
| Coverage | `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage` | PASS after root-route fix; reports starter-pack-only coverage |
| Quality report | `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report` | PASS endpoint, but report is not OK |
| Model providers | `curl -fsS http://127.0.0.1:8002/settings/model-providers` | PASS after root-route fix |
| Provider test | `curl -fsS -X POST http://127.0.0.1:8002/settings/model-providers/deterministic_baseline/test` | PASS |
| Evaluation | `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run` | PASS endpoint; metrics expose false-positive risk |
| Reports | `POST /reports/from-analysis` plus generated JSON/Markdown/HTML payloads | PASS after JSON limitation-note fix |
| Taxonomy export | `python scripts/export_taxonomy_excel.py /tmp/are-taxonomy-audit.xlsx` | PASS |
| Taxonomy import | Python `import_workbook('/tmp/are-taxonomy-audit.xlsx', temp_root)` | PASS mechanically; validation issues remain |
| Browser availability | `command -v google-chrome || command -v chromium || command -v chromium-browser` | WARNING: no Chrome/Chromium binary found in this environment |

## Issues

### AUD-001 — Fixed: HTTP server did not serve application routes

- severity: blocker
- file(s): `uvicorn/__init__.py`, `build_backend.py`
- problem: Before the fix, `uvicorn backend.app.main:app --reload` failed because no `uvicorn` console entry point was installed, and `python -m uvicorn ...` only returned a hard-coded response for `/health`.
- why it matters: The app could not satisfy the local-run requirement or the backend endpoint smoke tests via real HTTP.
- recommended fix: Completed in this branch. The local build backend now emits a `uvicorn` console entry point, and the shim dispatches GET/POST/PUT/PATCH requests to the app routes with JSON bodies, query params, path params, responses, and single-file multipart uploads.
- verification command: `pip install -e .[dev] && uvicorn backend.app.main:app --reload --port 8002` and `curl -fsS http://127.0.0.1:8002/analyze` with a JSON POST body.

### AUD-002 — Fixed: Requested root API paths were missing for taxonomy/workbench/settings

- severity: blocker
- file(s): `backend/app/main.py`
- problem: The app mounted taxonomy, taxonomy-workbench, and settings only under `/api`, while the audit required root paths such as `/taxonomy`, `/taxonomy-workbench/coverage`, and `/settings/model-providers`.
- why it matters: Operators following the documented audit commands would receive not-found responses for required endpoints.
- recommended fix: Completed in this branch. The same routers are mounted at both root and `/api` prefixes.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage`.

### AUD-003 — Fixed: JSON report lacked a limitations note

- severity: high
- file(s): `engine/argument_risk_engine/reports/json_export.py`, `engine/argument_risk_engine/reports/markdown.py`, `engine/argument_risk_engine/reports/html.py`
- problem: Markdown and HTML reports included the limitation text, but JSON exports returned only the raw analysis payload.
- why it matters: JSON is often the format most likely to be integrated downstream; omitting limitations increases misuse risk.
- recommended fix: Completed in this branch. JSON reports now include `limitations_note`; Markdown and HTML reuse the same constant.
- verification command: `python - <<'PY' ... render_json_report(...) ... PY` confirming the limitation note is present in all three formats.

### AUD-004 — Active dashboard taxonomy is only the starter pack

- severity: high
- file(s): `backend/app/core/paths.py`, `backend/app/services/taxonomy_service.py`, `data/taxonomy/packs/starter-pack.yaml`
- problem: The repository contains 1,103 taxonomy entries across pack files, but the API and dashboard load only `data/taxonomy/packs/starter-pack.yaml` as the active taxonomy. `/taxonomy-workbench/coverage` reported only 3 entries.
- why it matters: Taxonomy Browser, Taxonomy Workbench, analysis, and exports do not reflect the large taxonomy by default. This also hides large-taxonomy false-positive risk from dashboard users.
- recommended fix: Decide whether production default should be the curated starter pack or the reviewed active subset from all packs. If all packs are intended, change the service layer to use `load_all_packs()` plus active/enabled filtering, and add tests that deprecated/backlog/healthy entries are excluded.
- verification command: `python - <<'PY'\nfrom argument_risk_engine.taxonomy.pack_manager import load_all_packs\nprint(len(load_all_packs().entries))\nPY` and `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage`.

### AUD-005 — Starter taxonomy quality report fails

- severity: high
- file(s): `data/taxonomy/packs/starter-pack.yaml`, `engine/argument_risk_engine/taxonomy/quality_audit.py`, `engine/argument_risk_engine/taxonomy/validator.py`
- problem: `/taxonomy-workbench/quality-report` returned `ok: false`, 9 errors, and missing-example / missing-minimum-evidence / missing-false-positive-warning counts for the active starter entries.
- why it matters: Classification runs against entries that fail the project’s own active-classification quality gate.
- recommended fix: Add negative examples, minimum evidence requirements, and false-positive warnings to each active starter entry, or mark them review-required until quality gates pass.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report | python -m json.tool`.

### AUD-006 — Mini evaluation shows high false-positive rate

- severity: high
- file(s): `data/benchmarks/mini_eval_set.jsonl`, `engine/argument_risk_engine/classification/deterministic.py`, `engine/argument_risk_engine/scoring/scorer.py`, `data/taxonomy/packs/starter-pack.yaml`
- problem: `POST /evaluation/run` returned `label_precision: 0.4444`, `false_positive_rate: 0.5556`, and `over_classification_rate: 0.25`. Hard negatives containing words such as “always”, “never”, “all”, and “everyone” are flagged as overgeneralization.
- why it matters: The deterministic analyzer works without API keys, but its current active-pack behavior is not conservative enough for release claims about low false positives.
- recommended fix: Strengthen starter-pack minimum evidence requirements and negative examples, add lexical exclusions for quoted terms / policy statements / inventory statements, and require stronger evidence for high-sensitivity entries.
- verification command: `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run | python -m json.tool`.

### AUD-007 — Analyze endpoint does not actually use selected LLM providers

- severity: high
- file(s): `engine/argument_risk_engine/analyzer.py`, `backend/app/services/analyzer_service.py`, `engine/argument_risk_engine/classification/classifier.py`
- problem: `analyze_text()` always calls `classify_deterministic(...)`. Passing `mode="llm"` or a non-deterministic `model_provider_id` changes metadata/fallback flags but does not invoke `ArgumentRiskClassifier` or the configured provider.
- why it matters: This creates hidden model-switching ambiguity. Users can select/test providers, but analysis remains deterministic without a clear runtime warning.
- recommended fix: Either wire `analyze_text()` through `ArgumentRiskClassifier` with explicit failure/fallback reporting, or constrain the analyze API/UI to deterministic mode until provider-backed analysis is implemented.
- verification command: inspect `engine/argument_risk_engine/analyzer.py` and run `curl -fsS -H 'Content-Type: application/json' -d '{"text":"Everyone always caused this.","mode":"llm","model_provider_id":"openai_remote"}' http://127.0.0.1:8002/analyze | python -m json.tool`.

### AUD-008 — Chrome-specific usability was not fully verifiable in this environment

- severity: medium
- file(s): `frontend/scripts/dev_server.mjs`, `frontend/src/runtime-dashboard.js`, `frontend/src/App.tsx`
- problem: No Chrome/Chromium binary is installed in the execution environment, so I could verify the dashboard by HTTP, source inspection, and build only—not by an actual Chrome session.
- why it matters: Frontend regressions involving DOM interaction, file download prompts, file upload controls, and clipboard APIs can pass build/curl checks but fail in Chrome.
- recommended fix: Add Playwright or another headless browser smoke test to cover Analyze, model-provider dropdown, Taxonomy Browser, Workbench validate/import/export, Review save, Evaluation metrics, and Reports downloads.
- verification command: `command -v google-chrome || command -v chromium || command -v chromium-browser` and `cd frontend && npm run build`.

### AUD-009 — Served dashboard uses the runtime JavaScript app, not the React/Vite source tree

- severity: medium
- file(s): `frontend/index.html`, `frontend/scripts/dev_server.mjs`, `frontend/scripts/build_frontend.mjs`, `frontend/src/runtime-dashboard.js`, `frontend/src/App.tsx`
- problem: `index.html` loads `/app.js`, and the dev/build scripts map that to `src/runtime-dashboard.js`. The React source under `frontend/src/components` and `frontend/src/App.tsx` is not what the served app runs.
- why it matters: Developers may fix the React components and believe dashboard behavior changed, while production/dev output still uses the separate runtime dashboard implementation.
- recommended fix: Either switch the build/dev path to the React app or remove/clearly mark the unused React tree. Add a smoke test that asserts the served bundle is the intended dashboard implementation.
- verification command: `curl -fsS http://127.0.0.1:5173/app.js | head -5`.

### AUD-010 — External provider tests can attempt network calls without secrets

- severity: medium
- file(s): `engine/argument_risk_engine/classification/llm_client.py`, `backend/app/services/settings_service.py`, `data/config/model_profiles.yaml`
- problem: Testing `openai_remote` with no `OPENAI_API_KEY` produces a warning but still attempts model/chat endpoints, which failed in this environment with proxy 403s.
- why it matters: Local audits without secrets should not create surprising network traffic when the missing secret is already known.
- recommended fix: For remote providers, short-circuit provider tests when the declared API-key environment variable is unset unless the provider is explicitly marked as unauthenticated/local.
- verification command: `python - <<'PY'\nfrom backend.app.services.settings_service import test_model_provider\nprint(test_model_provider('openai_remote').model_dump())\nPY`.
