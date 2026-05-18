import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT))

from argument_risk_engine.taxonomy.importer import IMPORT_PATH, import_workbook  # noqa: E402

DEFAULT_INPUT = ROOT / "data/taxonomy/imports/argument_risk_taxonomy_living_workbook_v2_taxonomy_first.xlsx"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import an external taxonomy workbook into pack YAML files.")
    parser.add_argument("path", nargs="?", help="Deprecated positional input path; prefer --input.")
    parser.add_argument("--input", "-i", dest="input_path", help="Path to the user-managed .xlsx taxonomy workbook.")
    args = parser.parse_args()
    input_path = Path(args.input_path or args.path or DEFAULT_INPUT)
    if not input_path.exists():
        raise SystemExit(
            f"Workbook not found: {input_path}\n"
            "Place the user-managed workbook under data/taxonomy/imports/ or pass --input /path/to/workbook.xlsx.\n"
            "The real taxonomy workbook is intentionally not committed to Git."
        )
    report = import_workbook(input_path, ROOT)
    print(f"Copied workbook to {IMPORT_PATH}")
    print(f"Imported {report.entry_count} entries ({report.active_classification_count} active classification entries)")
    print(f"Validation: {len(report.errors)} errors, {len(report.warnings)} warnings")
