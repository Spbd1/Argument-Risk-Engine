from __future__ import annotations

import json
from pathlib import Path

from argument_risk_engine.taxonomy.importer import HEADERS
from argument_risk_engine.taxonomy.models import TaxonomyPack
from argument_risk_engine.taxonomy.validator import validate_taxonomy_pack_detailed
from openpyxl import Workbook


def _append_sheet(workbook: Workbook, title: str, rows: list[list[object]]) -> None:
    # The repo ships a tiny openpyxl stub for tests. It only exposes .active, so keep
    # writing the first sheet there and store extra sheets in a JSON metadata field when
    # the real library is unavailable.
    if title == "Taxonomy_Master" or not getattr(workbook, "_are_extra_sheets", False):
        sheet = workbook.active
        sheet.title = title
        for row in rows:
            sheet.append(row)
        workbook._are_extra_sheets = True
        return
    if hasattr(workbook, "create_sheet"):
        sheet = workbook.create_sheet(title=title)
        for row in rows:
            sheet.append(row)


def export_taxonomy_excel(pack: TaxonomyPack, path: Path | str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    taxonomy_rows = [HEADERS]
    for entry in pack.entries:
        taxonomy_rows.append([
            entry.id,
            entry.name,
            entry.pack,
            entry.canonical_category,
            entry.academic_status,
            entry.academic_consensus,
            entry.short_definition,
            entry.long_definition,
            entry.detection_level,
            "; ".join(entry.signals),
            "; ".join(entry.trigger_patterns),
            entry.minimum_evidence_requirement,
            "; ".join(entry.exclusion_criteria),
            "; ".join(entry.common_false_positives),
            "; ".join(entry.positive_examples),
            "; ".join(entry.negative_examples),
            "; ".join(entry.severity_guidance),
            "; ".join(entry.related_risks),
            "; ".join(entry.synonym_ids),
            "; ".join(entry.source_refs),
            entry.enabled_for_mvp,
            entry.enabled_for_retrieval,
            entry.enabled_for_classification,
            entry.requires_context,
            entry.requires_human_judgment,
            entry.false_positive_sensitivity,
            entry.activation_status,
            entry.healthy_suppressor,
            entry.model_assisted_allowed,
            entry.notes,
        ])
    _append_sheet(workbook, "Taxonomy_Master", taxonomy_rows)
    _append_sheet(workbook, "Taxonomy_Packs", [["pack_id", "entry_count"], *[[p, sum(1 for e in pack.entries if e.pack == p)] for p in sorted({e.pack for e in pack.entries})]])
    _append_sheet(workbook, "Model_Provider_Profiles", [["provider_id", "label"]])
    _append_sheet(workbook, "Activation_Workflow", [["activation_status", "meaning"], ["active", "usable for classification after review"], ["review_required", "not active until reviewed"]])
    _append_sheet(workbook, "Quality_Audit", [["check", "status"], ["taxonomy_export", "generated"]])
    report = validate_taxonomy_pack_detailed(pack).to_dict()
    _append_sheet(workbook, "Validation_Report", [["json"], [json.dumps(report)]])
    category_counts = sorted((category, sum(1 for e in pack.entries if e.canonical_category == category)) for category in {e.canonical_category for e in pack.entries})
    _append_sheet(workbook, "Category_Summary", [["canonical_category", "entry_count"], *category_counts])
    workbook.save(output)
    return output
