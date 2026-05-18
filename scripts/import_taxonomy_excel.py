import argparse
from pathlib import Path

from argument_risk_engine.taxonomy.importer import import_taxonomy_excel
from argument_risk_engine.taxonomy.loader import save_taxonomy_pack

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/taxonomy/imports/taxonomy.xlsx")
    args = parser.parse_args()
    pack = import_taxonomy_excel(ROOT / args.path)
    save_taxonomy_pack(pack, ROOT / "data/taxonomy/packs/starter-pack.yaml")
    print(f"Imported {len(pack.entries)} entries")
