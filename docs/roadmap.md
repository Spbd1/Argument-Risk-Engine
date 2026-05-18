# Roadmap

## Current MVP

- Local FastAPI backend.
- React dashboard for analysis, taxonomy workbench, settings, reports, evaluation, and review.
- File-backed taxonomy packs and settings.
- Deterministic baseline classifier.
- Excel taxonomy import/export.
- Mini benchmark and demo inputs.
- Docker Compose startup without a database.

## Near term

- Improve import validation messages and workbook schema documentation.
- Add more hard negatives and taxonomy-specific benchmark slices.
- Add provider-specific smoke tests for OpenAI-compatible endpoints.
- Improve report templates and citation formatting.
- Add dashboard status checks for backend/frontend connectivity.
- Add a packaged release workflow.

## Medium term

- Optional local model adapters.
- Better claim segmentation for long documents.
- Reviewer adjudication workflows.
- Taxonomy diffing and version comparison.
- More detailed calibration dashboards.
- Expanded accessibility and keyboard-navigation testing.

## Long term

- Optional database-backed multi-user mode.
- Pluggable authentication for deployments that need it.
- Auditable review trails.
- Larger, independently reviewed benchmark suites.
- Integration examples for document pipelines.

## Guardrails

The roadmap should not turn the project into automated moral judgment, truth determination, or automated moderation. Improvements should make the system more transparent, conservative, and reviewable.
