# Taxonomy Import/Export Report

## Scope

This report covers taxonomy IDs, pack validity, workbook import/export, source refs, healthy/deprecated/backlog exclusions, active/enabled classification filtering, and high false-positive sensitivity behavior.

## Verification summary

- `python scripts/export_taxonomy_excel.py /tmp/are-taxonomy-audit.xlsx` passed and produced a workbook file.
- Python `import_taxonomy_excel('/tmp/are-taxonomy-audit.xlsx')` loaded 1,103 workbook entries.
- Python `import_workbook('/tmp/are-taxonomy-audit.xlsx', temp_root)` completed mechanically with 1,103 entries and 49 active classification entries, but returned 9 validation errors and 23 warnings.
- `load_all_packs()` found 1,103 entries and no duplicate IDs.
- Healthy reasoning patterns had 0 entries enabled for classification.
- Deprecated entries had 0 active/enabled classification entries.
- Backlog exists as `data/taxonomy/candidate_backlog.yaml` and is not loaded by `load_all_packs()`.

## Issues

### TAX-001 — Active dashboard taxonomy is not the full pack set

- severity: high
- file(s): `backend/app/core/paths.py`, `backend/app/services/taxonomy_service.py`, `data/taxonomy/packs/starter-pack.yaml`
- problem: The dashboard/API active taxonomy points to only `starter-pack.yaml`; full pack import/export scripts handle 1,103 entries.
- why it matters: Workbench coverage/export from the dashboard can mislead users into thinking only 3 taxonomy entries exist.
- recommended fix: Add explicit active taxonomy configuration and label the dashboard coverage as starter-only if that remains the intended default.
- verification command: `curl -fsS http://127.0.0.1:8002/taxonomy-workbench/coverage | python -m json.tool`.

### TAX-002 — Workbook import/export works mechanically but validation fails

- severity: high
- file(s): `engine/argument_risk_engine/taxonomy/importer.py`, `engine/argument_risk_engine/taxonomy/exporter.py`, `engine/argument_risk_engine/taxonomy/validator.py`, `data/taxonomy/packs/starter-pack.yaml`
- problem: Round-trip import/export works, but validation reports active starter entries missing negative examples, minimum evidence requirements, and false-positive warnings.
- why it matters: A mechanically importable taxonomy can still be unsafe for classification.
- recommended fix: Treat validation failure as a release blocker for entries enabled for classification.
- verification command: `python scripts/export_taxonomy_excel.py /tmp/are-taxonomy-audit.xlsx && python - <<'PY' ... import_workbook(... temp_root) ... PY`.

### TAX-003 — Source refs are present in large packs but starter active entries are sparse

- severity: medium
- file(s): `data/taxonomy/packs/core_mvp.yaml`, `data/taxonomy/packs/starter-pack.yaml`, `engine/argument_risk_engine/taxonomy/source_registry.py`
- problem: Large-pack entries include source refs, while starter-pack entries are legacy/sparse and quality checks flag missing supporting metadata.
- why it matters: Active findings should be traceable to source refs or clear operational definitions.
- recommended fix: Migrate starter active entries to the v0.2 schema quality level or retire the starter pack as the dashboard default.
- verification command: `python - <<'PY'\nfrom argument_risk_engine.taxonomy.pack_manager import load_all_packs\nprint(load_all_packs().entries[0].source_refs)\nPY`.

### TAX-004 — Healthy/deprecated/backlog exclusions pass in code inspection but need API tests

- severity: medium
- file(s): `engine/argument_risk_engine/taxonomy/pack_manager.py`, `engine/argument_risk_engine/classification/classifier.py`, `data/taxonomy/candidate_backlog.yaml`
- problem: Code excludes healthy patterns and requires active/enabled entries, but tests should explicitly cover API/dashboard classification against full packs.
- why it matters: Future taxonomy imports could accidentally enable healthy or backlog entries for final risks.
- recommended fix: Add tests asserting healthy entries appear only as suppressors, deprecated/review/backlog entries never become final risks, and active/enabled is required.
- verification command: `python - <<'PY'\nfrom argument_risk_engine.taxonomy.pack_manager import load_all_packs, active_classification_entries\nprint(len(active_classification_entries(load_all_packs())))\nPY`.
