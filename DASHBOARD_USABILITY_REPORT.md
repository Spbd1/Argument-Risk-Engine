# Dashboard Usability Report

## Scope

This audit covered install/build/startup, dashboard serving, Analyze, model provider dropdown, Taxonomy Browser, Taxonomy Workbench validate/import/export, Model Settings, Review feedback, Evaluation metrics, and Reports downloads by source inspection and HTTP smoke checks. A real Chrome run was not possible because Chrome/Chromium is not installed in this environment.

## Verified

- `cd frontend && npm install` passed.
- `cd frontend && npm run build` passed.
- `cd frontend && npm run dev` served `http://localhost:5173`.
- `curl -fsS http://127.0.0.1:5173` returned the dashboard HTML.
- `curl -fsS http://127.0.0.1:5173/app.js` returned the runtime dashboard app.
- Backend routes used by the runtime dashboard are now reachable under `/api/*` and root aliases.

## Issues

### UI-001 — Chrome was unavailable for interactive verification

- severity: medium
- file(s): `frontend/src/runtime-dashboard.js`, `frontend/scripts/dev_server.mjs`
- problem: The environment has no `google-chrome`, `chromium`, or `chromium-browser` executable.
- why it matters: File upload/download behavior, navigation, select controls, clipboard, and alert-driven provider tests need browser automation or manual Chrome validation.
- recommended fix: Add Playwright/Chromium smoke tests to CI and document browser test commands.
- verification command: `command -v google-chrome || command -v chromium || command -v chromium-browser`.

### UI-002 — Served app bypasses React components

- severity: medium
- file(s): `frontend/index.html`, `frontend/scripts/dev_server.mjs`, `frontend/scripts/build_frontend.mjs`, `frontend/src/runtime-dashboard.js`, `frontend/src/App.tsx`
- problem: `index.html` loads `/app.js`; dev/build scripts serve/copy `src/runtime-dashboard.js`; React `App.tsx` is not the executed dashboard.
- why it matters: The UI has two implementations, increasing the risk of fixing or auditing the wrong one.
- recommended fix: Choose one implementation path. Prefer serving the React/Vite app if the React source is the maintained implementation.
- verification command: `curl -fsS http://127.0.0.1:5173/app.js | head -5`.

### UI-003 — Workbench import button does not guard against missing file selection

- severity: low
- file(s): `frontend/src/runtime-dashboard.js`
- problem: The import handler appends `file.files[0]` without a visible guard or user-friendly error when no file is selected.
- why it matters: A normal user mis-click can produce an opaque error.
- recommended fix: Disable the import button until a file is selected, or show a clear inline validation message.
- verification command: inspect `frontend/src/runtime-dashboard.js` import handler and run a browser interaction test.

### UI-004 — Reports page download buttons target the first report, not a selected report object

- severity: low
- file(s): `frontend/src/runtime-dashboard.js`
- problem: The report preview can be changed by clicking a list item, but download buttons are built from `state.reports[0]`.
- why it matters: Users may download a different report than the one they previewed.
- recommended fix: Track selected report ID in state and bind preview/download controls to the selected report.
- verification command: inspect `frontend/src/runtime-dashboard.js` reports page and add a browser test with two saved reports.
