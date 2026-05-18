from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

CLAIM_TYPES = {
    "causal_claim",
    "comparative_claim",
    "normative_claim",
    "generalization",
    "prediction",
    "recommendation",
    "evidential_claim",
    "statistical_claim",
    "analogy_claim",
    "question_claim",
    "descriptive_claim",
    "unclear",
}

_MARKERS: dict[str, tuple[str, ...]] = {
    "causal_claim": (
        "because",
        "therefore",
        "leads to",
        "causes",
        "results in",
        "due to",
        "explains",
        "responsible for",
    ),
    "comparative_claim": (
        "better than",
        "worse than",
        "more than",
        "less than",
        "superior",
        "inferior",
        "compared with",
    ),
    "normative_claim": ("should", "must", "ought", "need to", "have to"),
    "recommendation": ("recommend", "recommendation", "advise", "suggest", "best to"),
    "prediction": ("will", "likely", "expected to", "forecast", "probably"),
    "generalization": ("always", "never", "everyone", "no one", "all", "none", "most people"),
    "statistical_claim": ("percent", "average", "rate", "sample", "survey", "study", "data", "statistically"),
    "analogy_claim": ("like", "similar to", "just as", "equivalent to", "same as"),
    "evidential_claim": ("evidence", "according to", "shows", "found", "study", "data", "research"),
}

_STRONG_MARKER_TYPES = set(_MARKERS) | {"question_claim"}
_MEANINGFUL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])(?=\s|$)")


@dataclass(frozen=True)
class Claim(str):
    """A sentence-level claim that behaves like a string for legacy callers."""

    text: str = field(default="")
    start_char: int = 0
    end_char: int = 0
    claim_type: str = "unclear"
    markers: tuple[str, ...] = field(default_factory=tuple)

    def __new__(cls, text: str, start_char: int = 0, end_char: int | None = None, claim_type: str = "unclear", markers: Iterable[str] = ()):
        obj = str.__new__(cls, text)
        return obj

    def __init__(self, text: str, start_char: int = 0, end_char: int | None = None, claim_type: str = "unclear", markers: Iterable[str] = ()):
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "start_char", start_char)
        object.__setattr__(self, "end_char", len(text) + start_char if end_char is None else end_char)
        object.__setattr__(self, "claim_type", claim_type if claim_type in CLAIM_TYPES else "unclear")
        object.__setattr__(self, "markers", tuple(markers))

    def model_dump(self) -> dict[str, object]:
        return {
            "text": self.text,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "claim_type": self.claim_type,
            "markers": list(self.markers),
        }


def _meaningful_tokens(text: str) -> list[str]:
    return _MEANINGFUL_RE.findall(text)


def _contains_marker(text: str, marker: str) -> bool:
    pattern = r"(?<![A-Za-z0-9])" + re.escape(marker).replace(r"\ ", r"\s+") + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def detect_claim_type(sentence: str) -> tuple[str, tuple[str, ...]]:
    text = sentence.strip()
    if not text:
        return "unclear", ()
    if text.endswith("?"):
        return "question_claim", ()

    matched: dict[str, list[str]] = {}
    for claim_type, markers in _MARKERS.items():
        hits = [marker for marker in markers if _contains_marker(text, marker)]
        if hits:
            matched[claim_type] = hits

    if not matched:
        return ("descriptive_claim", ()) if len(_meaningful_tokens(text)) >= 5 else ("unclear", ())

    precedence = [
        "statistical_claim",
        "causal_claim",
        "comparative_claim",
        "normative_claim",
        "recommendation",
        "prediction",
        "generalization",
        "analogy_claim",
        "evidential_claim",
    ]
    for claim_type in precedence:
        if claim_type in matched:
            return claim_type, tuple(matched[claim_type])
    first_type = next(iter(matched))
    return first_type, tuple(matched[first_type])


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    cursor = 0
    for match in _SENTENCE_END_RE.finditer(text):
        end = match.end()
        raw = text[cursor:end]
        stripped = raw.strip()
        if stripped:
            start = cursor + len(raw) - len(raw.lstrip())
            finish = cursor + len(raw.rstrip())
            spans.append((text[start:finish], start, finish))
        cursor = end
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
    if cursor < len(text):
        raw = text[cursor:]
        for part in re.finditer(r"[^\n]+", raw):
            segment = part.group(0).strip()
            if segment:
                start = cursor + part.start() + len(part.group(0)) - len(part.group(0).lstrip())
                finish = cursor + part.end() - (len(part.group(0)) - len(part.group(0).rstrip()))
                spans.append((text[start:finish], start, finish))
    return spans


def extract_claims(text: str) -> list[Claim]:
    """Extract sentence-level claims with stable character offsets.

    Fragments with fewer than five meaningful tokens are ignored unless they contain
    one of the configured strong claim markers (or are questions).
    """

    if not text or not text.strip():
        return []

    claims: list[Claim] = []
    for sentence, start, end in _sentence_spans(text):
        claim_type, markers = detect_claim_type(sentence)
        strong = claim_type in _STRONG_MARKER_TYPES and (bool(markers) or claim_type == "question_claim")
        legacy_claim_label = bool(re.search(r"(?<![A-Za-z0-9])claims?(?![A-Za-z0-9])", sentence, flags=re.IGNORECASE))
        if len(_meaningful_tokens(sentence)) < 5 and not (strong or legacy_claim_label):
            continue
        claims.append(Claim(sentence, start, end, claim_type, markers))

    if claims:
        return claims

    stripped = text.strip()
    start = text.find(stripped)
    claim_type, markers = detect_claim_type(stripped)
    return [Claim(stripped, start, start + len(stripped), claim_type, markers)] if stripped else []
