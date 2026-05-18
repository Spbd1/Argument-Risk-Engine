from argument_risk_engine.taxonomy.loader import load_taxonomy_pack, save_taxonomy_pack
from argument_risk_engine.taxonomy.models import TaxonomyPack

from backend.app.core.paths import TAXONOMY_PACK_PATH


def get_active_pack() -> TaxonomyPack:
    return load_taxonomy_pack(TAXONOMY_PACK_PATH)


def save_active_pack(pack: TaxonomyPack) -> None:
    save_taxonomy_pack(pack, TAXONOMY_PACK_PATH)
