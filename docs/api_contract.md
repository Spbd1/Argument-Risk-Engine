# API Contract

The API is served by FastAPI at `http://localhost:8000`. Dashboard calls use the `/api` prefix; several legacy unprefixed routes also exist for compatibility.

## Health

### `GET /health`

Returns backend status.

```json
{"status":"ok"}
```

## Analysis

### `POST /api/analyze`

Request:

```json
{
  "text": "Everyone on the project always skips the checklist.",
  "top_k": 8,
  "include_retrieval_diagnostics": false
}
```

Response includes:

- `analysis_id`
- `text`
- `claims`
- `risks`
- `summary`
- `warnings`

Findings should include taxonomy IDs, labels, severity, confidence, evidence spans, and explanations.

## Taxonomy

### `GET /api/taxonomy`

Lists active taxonomy entries.

### `GET /api/taxonomy-workbench/packs`

Lists available local taxonomy packs.

### `POST /api/taxonomy-workbench/import-excel`

Multipart upload with form field `file`. Imports a user-managed `.xlsx` workbook.

### `GET /api/taxonomy-workbench/export-excel`

Downloads the current taxonomy as an Excel workbook.

### `POST /api/taxonomy-workbench/validate`

Validates current local taxonomy files without changing them.

## Settings

### `GET /api/settings/providers`

Lists model-provider profiles.

### `PUT /api/settings/providers/{provider_id}`

Saves provider metadata. Secrets should be supplied through environment variables, not committed YAML.

### `PUT /api/settings/active-provider`

Selects the active provider profile.

## Reports

### `GET /api/reports`

Lists generated reports.

### `POST /api/reports/from-analysis`

Creates Markdown, HTML, and/or JSON report artifacts from an analysis payload.

### `GET /api/reports/{report_id}/download?format=markdown`

Downloads a report artifact.

## Error handling

The MVP prefers readable JSON error objects. Clients should treat non-2xx responses as user-visible failures and should not silently ignore import, export, or report-generation errors.
