# Model Provider Security Report

## Scope

This report covers provider listing/testing, secret exposure, deterministic offline behavior, and hidden model switching.

## Verified

- `GET /settings/model-providers` returns provider metadata with `api_key_env_var` names but no raw secret fields.
- `POST /settings/model-providers/deterministic_baseline/test` returns `ok` without API keys.
- `patch_model_provider()` drops `api_key` and `raw_api_key` patch keys before persistence.
- Deterministic analysis works without API keys.

## Issues

### SEC-001 — Analyze does not use selected LLM provider despite provider settings

- severity: high
- file(s): `engine/argument_risk_engine/analyzer.py`, `backend/app/services/analyzer_service.py`, `engine/argument_risk_engine/classification/classifier.py`
- problem: Provider profiles can be selected/tested, but `analyze_text()` always uses `classify_deterministic(...)`.
- why it matters: This can mislead users and complicates auditability of whether model output was used.
- recommended fix: Wire provider selection into `ArgumentRiskClassifier`, or clearly disable model-backed analysis in the UI/API until implemented.
- verification command: `curl -fsS -H 'Content-Type: application/json' -d '{"text":"Everyone always caused this.","mode":"llm","model_provider_id":"openai_remote"}' http://127.0.0.1:8002/analyze | python -m json.tool`.

### SEC-002 — Remote provider tests attempt network calls when API key env var is missing

- severity: medium
- file(s): `engine/argument_risk_engine/classification/llm_client.py`, `backend/app/services/settings_service.py`
- problem: `openai_remote` test warns that `OPENAI_API_KEY` is unset but still attempts remote model/chat calls.
- why it matters: Missing-secret checks should be fail-fast for remote providers to avoid unintended traffic.
- recommended fix: Add a provider flag for unauthenticated local providers and short-circuit remote providers when the secret env var is absent.
- verification command: `python - <<'PY'\nfrom backend.app.services.settings_service import test_model_provider\nprint(test_model_provider('openai_remote').model_dump())\nPY`.

### SEC-003 — Secret names are exposed by design; raw secrets were not observed

- severity: low
- file(s): `backend/app/schemas/settings.py`, `backend/app/services/settings_service.py`, `data/config/model_profiles.yaml`
- problem: The API returns environment variable names such as `OPENAI_API_KEY`; this is acceptable metadata but should be documented as non-secret.
- why it matters: Operators should know raw keys belong only in environment variables or local `.env`, never in provider YAML or API responses.
- recommended fix: Add UI helper text that only env-var names are stored, and keep rejecting `api_key` / `raw_api_key` fields.
- verification command: `curl -fsS http://127.0.0.1:8002/settings/model-providers | python -m json.tool`.
