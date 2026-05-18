from argument_risk_engine.taxonomy.importer import import_taxonomy_excel

from openpyxl import Workbook


def test_import_taxonomy_excel(tmp_path):
    path = tmp_path / "taxonomy.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["id", "name", "description", "severity", "keywords", "examples", "mitigation", "active"])
    ws.append(["risk", "Risk", "Description", "low", "foo; bar", "foo example", "review", True])
    wb.save(path)
    pack = import_taxonomy_excel(path)
    assert pack.entries[0].keywords == ["foo", "bar"]
