# Taxonomy Design

Argument-Risk-Engine is taxonomy-first, evidence-grounded, conservative, and local-first. This document captures the MVP workflow and should be expanded as contributors add production features.


## Taxonomy workbook handling

The real taxonomy workbook should be imported later from the dashboard or CLI and is intentionally not committed to Git. Use the Chrome Taxonomy Workbench upload flow for interactive imports, or run `python scripts/import_taxonomy_excel.py --input data/taxonomy/imports/argument_risk_taxonomy_living_workbook_v2_taxonomy_first.xlsx` after placing the user-managed workbook at that path. Generated workbook exports and report artifacts remain local and ignored.
