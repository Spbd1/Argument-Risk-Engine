# False Positive Risks

## Summary

The deterministic analyzer is available offline and evidence-spans are exact substrings in the smoke checks. However, the active starter taxonomy and deterministic keyword matching still over-classify hard negatives in the bundled benchmark.

## Verification highlights

- Neutral text smoke: `The meeting starts at 10 AM and the agenda includes budget review.` produced 0 starter-pack risks.
- Healthy/cautious text smoke: `The pilot worked in one clinic, but the sample is small...` produced 0 starter-pack risks.
- Full-pack neutral smoke also produced 0 risks.
- Mini evaluation reported `false_positive_rate: 0.5556`, `label_precision: 0.4444`, and `over_classification_rate: 0.25`.
- Evidence spans in deterministic findings are exact substrings in the analyzed claim.
- LLM invented taxonomy labels are dropped by `ArgumentRiskClassifier` when not in supplied candidates.

## Issues

### FP-001 — Hard negatives with absolute words are classified as overgeneralization

- severity: high
- file(s): `engine/argument_risk_engine/classification/deterministic.py`, `data/benchmarks/mini_eval_set.jsonl`, `data/taxonomy/packs/starter-pack.yaml`
- problem: Evaluation false positives include operational/policy/inventory sentences containing words such as “always”, “never”, “all”, “none”, and “everyone”.
- why it matters: These words can be legitimate literal or procedural language, not argument-risk evidence.
- recommended fix: Add exclusion patterns for quoted/token examples, policy rules, inventory/checksum/log statements, and require broader claim context before overgeneralization labels.
- verification command: `curl -fsS -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8002/evaluation/run | python -m json.tool`.

### FP-002 — Active starter entries lack false-positive warnings and minimum evidence requirements

- severity: high
- file(s): `data/taxonomy/packs/starter-pack.yaml`, `engine/argument_risk_engine/taxonomy/validator.py`
- problem: Quality report flags all three active starter entries for missing false-positive warnings and minimum evidence requirements.
- why it matters: The classifier and UI cannot explain common safe contexts to reviewers.
- recommended fix: Fill these fields or disable the entries until reviewed.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/quality-report | python -m json.tool`.

### FP-003 — Large taxonomy is not aggressively classifying by default only because it is not active

- severity: medium
- file(s): `backend/app/core/paths.py`, `backend/app/services/taxonomy_service.py`, `engine/argument_risk_engine/taxonomy/pack_manager.py`
- problem: The dashboard's low large-taxonomy false-positive exposure comes from using `starter-pack.yaml`, not from exercising all active/enabled entries in the large taxonomy.
- why it matters: Switching to all packs later could introduce new false positives unless retrieval and scoring are tested against the large active subset.
- recommended fix: Add full-pack evaluation runs and compare hard-negative false positive rates before changing active taxonomy defaults.
- verification command: `python - <<'PY'\nfrom argument_risk_engine.analyzer import analyze_text\nfrom argument_risk_engine.taxonomy.pack_manager import load_all_packs\nprint(analyze_text('The meeting starts at 10 AM and the agenda includes budget review.', load_all_packs(), top_k=20)['risk_level'])\nPY`.

### FP-004 — Short-claim cap exists but should be tested at API level

- severity: low
- file(s): `engine/argument_risk_engine/analyzer.py`, `engine/argument_risk_engine/scoring/scorer.py`, `tests/test_scorer.py`
- problem: The analyzer truncates risks to `max_risks_per_claim`, and scoring has short-claim guardrails, but the API does not have a dedicated regression for the “max 3 risks” release requirement.
- why it matters: API parameter changes could bypass conservative short-claim behavior.
- recommended fix: Add an API test asserting short claims cannot return more than 3 final risks under default settings.
- verification command: `pytest tests/test_scorer.py tests/test_api_analysis.py`.
