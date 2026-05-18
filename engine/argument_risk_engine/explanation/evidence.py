from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvidenceSpan:
    text: str
    start_char: int
    end_char: int
    source: str = "input_text"
    match_type: str = "exact"
    confidence: float = 1.0

    @property
    def quote(self) -> str:
        return self.text

    @property
    def start(self) -> int:
        return self.start_char

    @property
    def end(self) -> int:
        return self.end_char

    def __getitem__(self, key: str) -> object:
        aliases = {"quote": "text", "start": "start_char", "end": "end_char"}
        return getattr(self, aliases.get(key, key))

    def get(self, key: str, default: object = None) -> object:
        try:
            return self[key]
        except AttributeError:
            return default

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data.update({"quote": self.text, "start": self.start_char, "end": self.end_char})
        return data


def find_evidence_spans(text: str, evidence_text: str, *, source: str = "input_text", match_type: str = "exact") -> list[EvidenceSpan]:
    """Return exact evidence spans from text; never fabricate missing evidence."""

    if not text or not evidence_text:
        return []
    start = text.find(evidence_text)
    if start < 0:
        normalized = evidence_text.strip()
        start = text.find(normalized) if normalized else -1
        evidence_text = normalized
    if start < 0:
        return []
    end = start + len(evidence_text)
    if text[start:end] != evidence_text:
        return []
    return [EvidenceSpan(evidence_text, start, end, source=source, match_type=match_type, confidence=1.0)]


def evidence_span(text: str, claim: str) -> dict[str, object]:
    spans = find_evidence_spans(text, str(claim))
    if not spans:
        return {}
    return spans[0].to_dict()
