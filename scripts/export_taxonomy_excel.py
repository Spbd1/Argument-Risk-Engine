import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT))

from argument_risk_engine.taxonomy.exporter import export_taxonomy_excel  # noqa: E402
from argument_risk_engine.taxonomy.pack_manager import load_all_packs  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export current taxonomy packs back to an Excel workbook.")
    parser.add_argument("path", nargs="?", default="data/taxonomy/exports/taxonomy.xlsx")
    args = parser.parse_args()
    out = export_taxonomy_excel(load_all_packs(ROOT / "data/taxonomy/packs"), ROOT / args.path)
    print(out)
