from pathlib import Path

from argument_risk_engine.taxonomy.loader import save_taxonomy_pack
from argument_risk_engine.taxonomy.models import default_taxonomy_pack

ROOT = Path(__file__).resolve().parents[1]


def seed() -> None:
    save_taxonomy_pack(default_taxonomy_pack(), ROOT / "data/taxonomy/packs/starter-pack.yaml")
    files = {
        "data/taxonomy/source_registry.yaml": "sources: []\n",
        "data/taxonomy/synonym_map.yaml": "synonyms: {}\n",
        "data/taxonomy/candidate_backlog.yaml": "candidates: []\n",
        "data/config/model_profiles.yaml": "profiles:\n  deterministic:\n    provider: deterministic\n    model: local-keyword\n",
        "data/config/app_settings.yaml": "llm_provider: deterministic\n",
        "data/examples/demo_inputs.jsonl": '{"text":"Everyone always caused this problem because of that policy."}\n',
        "data/benchmarks/mini_eval_set.jsonl": '{"text":"They are vermin.","expected":["dehumanizing_language"]}\n',
        "data/review/review_store.jsonl": "",
    }
    for rel, content in files.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content)
    (ROOT / "data/taxonomy/imports").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/reports").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    seed()
    print("Demo data seeded.")
