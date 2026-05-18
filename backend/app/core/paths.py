from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
TAXONOMY_PACK_PATH = DATA_DIR / "taxonomy" / "packs" / "starter-pack.yaml"
REVIEW_STORE_PATH = DATA_DIR / "review" / "review_store.jsonl"
REPORTS_DIR = DATA_DIR / "reports"
