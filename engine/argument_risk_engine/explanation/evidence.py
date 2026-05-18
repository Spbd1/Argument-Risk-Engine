from __future__ import annotations


def evidence_span(text: str, claim: str) -> dict[str, object]:
    start = text.find(claim)
    return {"quote": claim, "start": max(start, 0), "end": max(start, 0) + len(claim)}
