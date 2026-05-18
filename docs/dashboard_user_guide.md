# Dashboard User Guide

The dashboard is designed for Chrome at <http://localhost:5173> after the backend starts on <http://localhost:8000>.

## Start the dashboard

Recommended:

```bash
python scripts/dev.py --install --run --open
```

Manual:

```bash
python scripts/run_backend.py
cd frontend && npm run dev
```

## Analyze text

1. Open **Analyze**.
2. Paste or type text.
3. Click the analyze button.
4. Review extracted claims.
5. Inspect each risk card’s taxonomy label, evidence span, confidence, severity, and explanation.
6. Use export/report controls to save review artifacts.

Use outputs as review aids only. Do not treat them as truth or intent judgments.

## Configure model provider

1. Open **Model Settings**.
2. Review the deterministic baseline profile.
3. Add or edit an OpenAI-compatible provider if needed.
4. Store secrets in `.env` or environment variables, not in committed files.
5. Test the provider from the dashboard.
6. Select the active provider.

The deterministic baseline is safest for local demos because it has no network dependency.

## Import/export taxonomy Excel

1. Open **Taxonomy Workbench**.
2. In **Taxonomy import/export**, choose a `.xlsx` workbook.
3. Click **Import Excel**.
4. Review errors and warnings.
5. Click **Validate taxonomy**.
6. Click **Export Excel** to download the current local taxonomy.

The real taxonomy workbook is user-managed and intentionally not committed to Git.

## Generate reports

1. Analyze text.
2. Save a report from the analysis view.
3. Open **Reports**.
4. Preview Markdown, HTML, or JSON.
5. Download the desired format.

Reports are written under `data/reports/` for local use.

## Run evaluation from Chrome

Open **Evaluation** and run or refresh the mini benchmark view. Use it to inspect false positives, false negatives, and evidence-span issues after taxonomy or classifier changes.

## Review queue

Open **Review** to inspect persisted review examples from `data/review/review_store.jsonl`. This is a lightweight MVP workflow, not a full adjudication system.

## Troubleshooting

- Backend health: <http://localhost:8000/health>
- Frontend: <http://localhost:5173>
- Reinstall dependencies: `python scripts/bootstrap.py`
- Reseed demo data: `python scripts/seed_demo_data.py`
- Run tests: `make test`
