from __future__ import annotations

import json
from typing import Any


def render_json_report(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
