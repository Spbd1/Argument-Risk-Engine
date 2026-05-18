from __future__ import annotations

import json
import re
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import yaml

from argument_risk_engine.taxonomy.models import (
    AcademicStatus,
    CanonicalCategory,
    TaxonomyEntry,
    TaxonomyPack,
    normalize_id,
    parse_bool,
    split_list,
)
from argument_risk_engine.taxonomy.validator import TaxonomyValidationReport, validate_taxonomy_pack_detailed

ROOT = Path(__file__).resolve().parents[3]
IMPORT_PATH = ROOT / "data/taxonomy/imports/argument_risk_taxonomy_living_workbook_v2_taxonomy_first.xlsx"
PACKS_DIR = ROOT / "data/taxonomy/packs"
REPORT_PATH = ROOT / "data/reports/taxonomy_validation_report.json"
SOURCE_REGISTRY_PATH = ROOT / "data/taxonomy/source_registry.yaml"
MODEL_PROFILES_PATH = ROOT / "data/config/model_profiles.yaml"

HEADERS = [
    "id", "name", "pack", "canonical_category", "academic_status", "academic_consensus",
    "short_definition", "long_definition", "detection_level", "signals", "trigger_patterns",
    "minimum_evidence_requirement", "exclusion_criteria", "common_false_positives",
    "positive_examples", "negative_examples", "severity_guidance", "related_risks",
    "synonym_ids", "source_refs", "enabled_for_mvp", "enabled_for_retrieval",
    "enabled_for_classification", "requires_context", "requires_human_judgment",
    "false_positive_sensitivity", "activation_status", "healthy_suppressor",
    "model_assisted_allowed", "notes",
]

@dataclass
class Sheet:
    title: str
    rows: list[list[object]]


def _column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref or "A").group(0)
    index = 0
    for char in letters:
        index = index * 26 + ord(char) - 64
    return index - 1


def _read_xlsx(path: Path) -> dict[str, Sheet]:
    try:
        # Compatibility with the repo's tiny openpyxl test stub, which writes JSON files.
        data = json.loads(path.read_text())
        if "rows" in data:
            return {"Taxonomy_Master": Sheet("Taxonomy_Master", data["rows"]), "taxonomy": Sheet("taxonomy", data["rows"])}
    except Exception:
        pass

    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    with ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root.findall(ns + "si"):
                shared.append("".join(t.text or "" for t in si.iter(ns + "t")))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"].lstrip("/") for rel in rels}
        sheets: dict[str, Sheet] = {}
        for sheet_node in workbook.find(ns + "sheets"):
            name = sheet_node.attrib["name"]
            rid = sheet_node.attrib[rel_ns + "id"]
            target = rel_map[rid]
            xml_path = target if target.startswith("xl/") else f"xl/{target}"
            root = ET.fromstring(archive.read(xml_path))
            rows: list[list[object]] = []
            for row_node in root.findall(".//" + ns + "row"):
                cells: dict[int, object] = {}
                for cell in row_node.findall(ns + "c"):
                    value_node = cell.find(ns + "v")
                    inline_node = cell.find(ns + "is")
                    value = ""
                    if value_node is not None:
                        value = value_node.text or ""
                        if cell.attrib.get("t") == "s" and value != "":
                            value = shared[int(value)]
                    elif inline_node is not None:
                        value = "".join(t.text or "" for t in inline_node.iter(ns + "t"))
                    cells[_column_index(cell.attrib.get("r", "A"))] = value
                if cells:
                    max_idx = max(cells)
                    rows.append([cells.get(i, "") for i in range(max_idx + 1)])
            sheets[name] = Sheet(name, rows)
        return sheets


def _row_dicts(sheet: Sheet) -> list[tuple[int, dict[str, object]]]:
    if not sheet.rows:
        return []
    headers = [normalize_id(cell) for cell in sheet.rows[0]]
    items = []
    for row_number, row in enumerate(sheet.rows[1:], start=2):
        if not any(str(cell).strip() for cell in row):
            continue
        items.append((row_number, {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}))
    return items


def _category(row: dict[str, object]) -> str:
    macro = normalize_id(row.get("macro_category"))
    sub = normalize_id(row.get("subcategory"))
    text = f"{macro} {sub} {normalize_id(row.get('tax_id'))}"
    if "healthy" in text:
        return CanonicalCategory.healthy_reasoning_pattern.value
    if "bias" in text and "cognitive" in text:
        return CanonicalCategory.cognitive_bias.value
    if "bias" in text and ("behaviour" in text or "behavior" in text):
        return CanonicalCategory.behavioural_bias.value
    if "causal" in text or "causation" in text:
        return CanonicalCategory.causal_reasoning_error.value
    if "statistical" in text or "statistics" in text:
        return CanonicalCategory.statistical_reasoning_error.value
    if "evidence" in text:
        return CanonicalCategory.evidence_failure.value
    if "uncertainty" in text:
        return CanonicalCategory.uncertainty_failure.value
    if "rhetoric" in text:
        return CanonicalCategory.rhetorical_pattern.value
    if "social" in text:
        return CanonicalCategory.social_influence_pattern.value
    if "manipulation" in text:
        return CanonicalCategory.manipulation_pattern.value
    if "fallac" in text or "reasoning_failure" in text or macro == "reasoning_failures":
        return CanonicalCategory.fallacy.value
    return CanonicalCategory.operational_detection_category.value


def _detection_level(value: object) -> str:
    normalized = normalize_id(value)
    return {
        "dialogue": "discourse",
        "formal": "structural",
        "claim": "structural",
        "multi_claim": "cross_claim",
    }.get(normalized, normalized or "contextual")


def _entry_from_workbook_row(row_number: int, row: dict[str, object]) -> TaxonomyEntry:
    tax_id = row.get("tax_id") or row.get("id")
    source_family = row.get("source_family")
    source_refs = split_list(source_family) or split_list(row.get("source_refs"))
    if row.get("primary_source_url"):
        source_refs.extend(split_list(row.get("primary_source_url")))
    academic_status = normalize_id(row.get("academic_status_v2") or row.get("academic_status") or row.get("taxonomy_status"))
    if academic_status not in {item.value for item in AcademicStatus}:
        academic_status = AcademicStatus.operational.value
    return TaxonomyEntry(
        id=tax_id,
        name=row.get("parent_label_en") or row.get("name") or tax_id,
        pack=row.get("pack_v2") or row.get("pack") or "core_mvp",
        canonical_category=row.get("canonical_category") or _category(row),
        academic_status=academic_status,
        academic_consensus=row.get("academic_consensus") or "operational_only",
        short_definition=row.get("definition_draft") or row.get("short_definition") or row.get("description") or "",
        long_definition=row.get("long_definition") or row.get("definition_draft") or "",
        detection_level=_detection_level(row.get("detection_level")),
        signals=row.get("linguistic_or_structural_signals") or row.get("signals") or row.get("keywords") or "",
        trigger_patterns=row.get("trigger_patterns") or "",
        minimum_evidence_requirement=row.get("minimum_evidence_required") or row.get("minimum_evidence_requirement") or "",
        exclusion_criteria=row.get("exclusion_criteria") or "",
        common_false_positives=row.get("false_positive_guard") or row.get("common_false_positives") or "",
        positive_examples=row.get("positive_example_stub") or row.get("positive_examples") or row.get("examples") or "",
        negative_examples=row.get("negative_example_stub") or row.get("negative_examples") or "",
        severity_guidance=split_list(row.get("severity_low")) + split_list(row.get("severity_medium")) + split_list(row.get("severity_high")),
        related_risks=row.get("related_family_ids") or row.get("related_risks") or "",
        synonym_ids=row.get("synonym_ids") or "",
        source_refs=source_refs,
        enabled_for_mvp=row.get("enabled_for_mvp"),
        enabled_for_retrieval=row.get("enabled_for_retrieval"),
        enabled_for_classification=row.get("enabled_for_classification"),
        requires_context=row.get("requires_context"),
        requires_human_judgment=row.get("requires_human_judgment"),
        false_positive_sensitivity=row.get("false_positive_sensitivity") or "medium",
        activation_status=row.get("activation_status") or "review_required",
        healthy_suppressor=row.get("healthy_suppressor"),
        model_assisted_allowed=row.get("model_assisted_allowed"),
        notes=row.get("notes_for_review") or row.get("notes") or "",
        row_number=row_number,
        metadata={
            "workbook_row_number": row_number,
            "source_family": source_family or "",
            "codex_import_action": row.get("codex_import_action") or "",
        },
    )


def import_taxonomy_excel(path: Path | str) -> TaxonomyPack:
    sheets = _read_xlsx(Path(path))
    sheet = sheets.get("Taxonomy_Master") or sheets.get("taxonomy") or next(iter(sheets.values()))
    entries = [_entry_from_workbook_row(row_number, row) for row_number, row in _row_dicts(sheet)]
    return TaxonomyPack(name=Path(path).stem, version="0.2.0", entries=entries, metadata={"source_workbook": str(path)})


def import_workbook(path: Path | str, root: Path = ROOT) -> TaxonomyValidationReport:
    source = Path(path)
    import_target = root / IMPORT_PATH.relative_to(ROOT)
    import_target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != import_target.resolve():
        shutil.copy2(source, import_target)
    sheets = _read_xlsx(import_target)
    pack = import_taxonomy_excel(import_target)
    report = validate_taxonomy_pack_detailed(pack)

    pack_dir = root / "data/taxonomy/packs"
    pack_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[TaxonomyEntry]] = {}
    for entry in pack.entries:
        grouped.setdefault(entry.pack, []).append(entry)
    for pack_id, entries in sorted(grouped.items()):
        data = TaxonomyPack(name=pack_id, version=pack.version, entries=entries).model_dump(mode="json")
        (pack_dir / f"{pack_id}.yaml").write_text(yaml.safe_dump(data, sort_keys=False))

    _write_sheet_yaml(sheets, "Source_Registry_Extended", root / "data/taxonomy/source_registry.yaml")
    _write_sheet_yaml(sheets, "Model_Provider_Profiles", root / "data/config/model_profiles.yaml")
    report_path = root / "data/reports/taxonomy_validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report.to_dict(), indent=2))
    return report


def _write_sheet_yaml(sheets: dict[str, Sheet], name: str, path: Path) -> None:
    sheet = sheets.get(name)
    rows = [] if not sheet else [row for _, row in _row_dicts(sheet)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"version": "0.2.0", "items": rows}, sort_keys=False))
