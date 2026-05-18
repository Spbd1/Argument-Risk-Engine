import argparse
from pathlib import Path

from argument_risk_engine.taxonomy.exporter import export_taxonomy_excel
from argument_risk_engine.taxonomy.loader import load_taxonomy_pack

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/taxonomy/exports/taxonomy.xlsx")
    args = parser.parse_args()
    out = export_taxonomy_excel(load_taxonomy_pack(ROOT / "data/taxonomy/packs/starter-pack.yaml"), ROOT / args.path)
    print(out)
