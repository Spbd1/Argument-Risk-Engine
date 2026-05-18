from __future__ import annotations

import json
from pathlib import Path

from argument_risk_engine.analyzer import analyze_text


def run_evaluation(path: Path | str) -> dict[str, object]:
    rows = []
    p = Path(path)
    if p.exists():
        rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    analyses = [analyze_text(row.get("text", "")) for row in rows]
    return {"items": len(rows), "analyses": analyses}
