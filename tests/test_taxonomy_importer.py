from argument_risk_engine.taxonomy.importer import import_taxonomy_excel

from openpyxl import Workbook


def test_import_taxonomy_excel(tmp_path):
    path = tmp_path / "taxonomy.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["id", "name", "description", "severity", "keywords", "examples", "mitigation", "active"])
    ws.append(["Risk ID", "Risk", "Description", "low", "foo; bar", "foo example", "review", True])
    wb.save(path)
    pack = import_taxonomy_excel(path)
    assert pack.entries[0].id == "risk_id"
    assert pack.entries[0].keywords == ["foo", "bar"]


def test_import_preserves_workbook_row_number(tmp_path):
    path = tmp_path / "taxonomy.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["tax_id", "parent_label_en", "pack_v2", "activation_status"])
    ws.append(["", "", "", ""])
    ws.append(["Needs Review", "Needs Review", "Core", "review_required"])
    wb.save(path)
    pack = import_taxonomy_excel(path)
    assert pack.entries[0].row_number == 3
