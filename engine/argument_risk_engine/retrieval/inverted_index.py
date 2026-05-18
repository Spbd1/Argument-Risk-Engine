from __future__ import annotations

import re
from collections import defaultdict

TOKEN_RE = re.compile(r"[a-z0-9_']+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class InvertedIndex:
    def __init__(self) -> None:
        self.index: dict[str, set[str]] = defaultdict(set)

    def add(self, doc_id: str, text: str) -> None:
        for token in tokenize(text):
            self.index[token].add(doc_id)

    def search(self, text: str) -> set[str]:
        matches: set[str] = set()
        for token in tokenize(text):
            matches.update(self.index.get(token, set()))
        return matches
