from __future__ import annotations

import json
from typing import Any

LIMITATIONS_NOTE = "Metrics and reports are review aids only and do not claim scientific validation."


def render_json_report(result: dict[str, Any]) -> str:
    payload = dict(result)
    payload.setdefault("limitations_note", LIMITATIONS_NOTE)
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
