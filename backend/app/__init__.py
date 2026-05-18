from __future__ import annotations

import sys
from pathlib import Path

_ENGINE_PATH = Path(__file__).resolve().parents[2] / "engine"
if _ENGINE_PATH.exists() and str(_ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(_ENGINE_PATH))
