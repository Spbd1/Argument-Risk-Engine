from __future__ import annotations

import re


def extract_claims(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    claims = [piece.strip() for piece in pieces if len(piece.strip()) >= 8]
    return claims or ([text.strip()] if text.strip() else [])
