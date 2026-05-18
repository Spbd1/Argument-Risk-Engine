# Prioritized Fixes

## P0 / blockers fixed in this branch

### P0-1: Make the documented backend server command runnable

- severity: blocker
- file(s): `build_backend.py`, `uvicorn/__init__.py`
- problem: `uvicorn backend.app.main:app --reload` was not available after editable install, and the server shim did not dispatch app routes.
- why it matters: Local installation/run and HTTP smoke tests were blocked.
- recommended fix: Done. Keep the console entry point and route-dispatching shim covered by smoke tests.
- verification command: `pip install -e .[dev] && uvicorn backend.app.main:app --reload --port 8002`.

### P0-2: Mount required non-`/api` routes

- severity: blocker
- file(s): `backend/app/main.py`
- problem: Required audit endpoints under `/taxonomy`, `/taxonomy-workbench`, and `/settings` were missing at root.
- why it matters: Backend audit commands failed even though `/api/*` routes existed.
- recommended fix: Done. Maintain both root and `/api` aliases unless the API contract is revised.
- verification command: `curl -fsS http://127.0.0.1:8002/settings/model-providers`.

## P1 / should fix before release

### P1-1: Decide and implement active taxonomy semantics

- severity: high
- file(s): `backend/app/core/paths.py`, `backend/app/services/taxonomy_service.py`, `backend/app/services/taxonomy_workbench_service.py`
- problem: The active API/dashboard taxonomy is `starter-pack.yaml` only, while the repository contains a much larger taxonomy.
- why it matters: Operators cannot audit or use the large taxonomy through the dashboard unless they import it into the starter path.
- recommended fix: Introduce an explicit active-taxonomy config: `starter`, `all_packs_active_enabled`, or `imported_workbook`. Add tests for each mode.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage | python -m json.tool`.

### P1-2: Make active taxonomy quality pass or deactivate weak entries

- severity: high
- file(s): `data/taxonomy/packs/starter-pack.yaml`, `engine/argument_risk_engine/taxonomy/validator.py`
- problem: Active entries fail validation for missing negative examples, minimum evidence, and false-positive warnings.
- why it matters: Quality gates do not protect users from known weak entries.
- recommended fix: Complete each active entry or set it to `review_required` / `enabled_for_classification: false`.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report | python -m json.tool`.

### P1-3: Reduce deterministic false positives on hard negatives

- severity: high
- file(s): `engine/argument_risk_engine/classification/deterministic.py`, `engine/argument_risk_engine/scoring/scorer.py`, `data/benchmarks/mini_eval_set.jsonl`
- problem: The mini benchmark reported a 0.5556 false-positive rate.
- why it matters: Conservative behavior is a release requirement.
- recommended fix: Add stronger evidence gates, hard-negative exclusions, and calibrated suppression for high-sensitivity entries.
- verification command: `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run | python -m json.tool`.

### P1-4: Remove hidden provider-mode ambiguity in analysis

- severity: high
- file(s): `engine/argument_risk_engine/analyzer.py`, `backend/app/services/analyzer_service.py`, `engine/argument_risk_engine/classification/classifier.py`
- problem: Provider settings can be selected/tested, but `analyze_text()` remains deterministic.
- why it matters: Users may believe a selected provider is analyzing text when it is not.
- recommended fix: Wire analyze through `ArgumentRiskClassifier`, or disable/label provider-backed analysis as unavailable.
- verification command: `curl -fsS -H 'Content-Type: application/json' -d '{"text":"Everyone always caused this.","mode":"llm","model_provider_id":"openai_remote"}' http://127.0.0.1:8002/analyze | python -m json.tool`.

## P2 / important usability and security hardening

### P2-1: Add browser automation smoke tests

- severity: medium
- file(s): `frontend/src/runtime-dashboard.js`, `frontend/scripts/dev_server.mjs`
- problem: Chrome was not available in this environment; no browser automation exists.
- why it matters: Build success does not prove Analyze, imports, exports, review saves, and downloads work in Chrome.
- recommended fix: Add Playwright tests for the required frontend flows.
- verification command: future `npx playwright test`.

### P2-2: Consolidate frontend implementation path

- severity: medium
- file(s): `frontend/index.html`, `frontend/src/runtime-dashboard.js`, `frontend/src/App.tsx`
- problem: Served app uses runtime JS, not the React component tree.
- why it matters: Maintenance changes can land in the wrong UI implementation.
- recommended fix: Serve/build the React app or remove stale React components.
- verification command: `curl -fsS http://127.0.0.1:5173/app.js | head -5`.

### P2-3: Avoid remote provider test network calls when API key is missing

- severity: medium
- file(s): `engine/argument_risk_engine/classification/llm_client.py`
- problem: Remote provider tests warn about missing keys but still attempt network calls.
- why it matters: Local audits should avoid surprising external traffic.
- recommended fix: Short-circuit remote tests when the configured secret env var is absent.
- verification command: `python - <<'PY'\nfrom backend.app.services.settings_service import test_model_provider\nprint(test_model_provider('openai_remote').model_dump())\nPY`.
