from __future__ import annotations

from pathlib import Path

from argument_risk_engine.taxonomy.importer import HEADERS
from argument_risk_engine.taxonomy.models import TaxonomyPack
from openpyxl import Workbook


def export_taxonomy_excel(pack: TaxonomyPack, path: Path | str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "taxonomy"
    sheet.append(HEADERS)
    for entry in pack.entries:
        sheet.append([
            entry.id,
            entry.name,
            entry.description,
            entry.severity.value,
            "; ".join(entry.keywords),
            "; ".join(entry.examples),
            entry.mitigation,
            entry.active,
        ])
    workbook.save(output)
    return output
