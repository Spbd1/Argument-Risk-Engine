from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from argument_risk_engine.taxonomy.models import ActivationStatus, TaxonomyEntry, TaxonomyPack

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_'-]*")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "into", "is", "it", "its", "of", "on", "or", "that", "the", "their", "them", "then", "there", "these", "this", "those", "to", "was", "were", "with", "without", "we", "you", "they", "i",
}

GENERIC_TERMS = {
    "argument", "claim", "claims", "evidence", "reason", "reasoning", "risk", "risks", "statement", "statements", "language", "pattern", "patterns", "people", "person", "group", "thing", "things", "good", "bad", "better", "worse", "issue", "case", "example", "examples", "support", "supports", "may", "might", "could", "would", "should",
}

FIELD_WEIGHTS = {
    "name": 3.0,
    "synonyms": 3.0,
    "signals": 4.0,
    "trigger_patterns": 5.0,
    "definitions": 1.25,
}


def tokenize(text: str, *, keep_generic: bool = True) -> list[str]:
    tokens = TOKEN_RE.findall(str(text).lower())
    if keep_generic:
        return tokens
    return [token for token in tokens if token not in STOPWORDS and token not in GENERIC_TERMS and len(token) > 1]


def normalize_phrase(text: str) -> str:
    return " ".join(tokenize(text, keep_generic=True))


def significant_terms(text: str) -> list[str]:
    return tokenize(text, keep_generic=False)


@dataclass(frozen=True)
class IndexedField:
    field: str
    value: str
    terms: tuple[str, ...]
    phrase: str


@dataclass
class IndexedEntry:
    entry: TaxonomyEntry
    fields: list[IndexedField] = field(default_factory=list)
    is_healthy_suppressor: bool = False
    is_candidate_only: bool = False


class InvertedIndex:
    def __init__(self, pack: TaxonomyPack | None = None) -> None:
        self.index: dict[str, set[str]] = defaultdict(set)
        self.entries: dict[str, IndexedEntry] = {}
        self.ignored_terms: set[str] = set(STOPWORDS | GENERIC_TERMS)
        if pack is not None:
            self.build(pack)

    def add(self, doc_id: str, text: str) -> None:
        for token in significant_terms(text):
            self.index[token].add(doc_id)

    def build(self, pack: TaxonomyPack) -> None:
        for entry in pack.entries:
            if not _retrievable(entry):
                continue
            indexed = IndexedEntry(
                entry=entry,
                is_healthy_suppressor=_is_healthy_suppressor(entry),
                is_candidate_only=bool(entry.enabled_for_retrieval and not entry.enabled_for_classification),
            )
            for field_name, value in _entry_field_values(entry):
                terms = tuple(significant_terms(value))
                phrase = normalize_phrase(value)
                if not terms and not phrase:
                    continue
                indexed.fields.append(IndexedField(field_name, value, terms, phrase))
                for term in terms:
                    self.index[term].add(entry.id)
            if indexed.fields:
                self.entries[entry.id] = indexed

    def search(self, text: str) -> set[str]:
        matches: set[str] = set()
        for token in significant_terms(text):
            matches.update(self.index.get(token, set()))
        return matches

    def get(self, doc_id: str) -> IndexedEntry | None:
        return self.entries.get(doc_id)


def _list_from_metadata(entry: TaxonomyEntry, key: str) -> list[str]:
    value = entry.metadata.get(key) if entry.metadata else None
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def _entry_field_values(entry: TaxonomyEntry) -> Iterable[tuple[str, str]]:
    yield "name", entry.name
    for synonym in [*entry.synonym_ids, *_list_from_metadata(entry, "synonyms")]:
        yield "synonyms", synonym
    for signal in entry.signals:
        yield "signals", signal
    for trigger in entry.trigger_patterns:
        yield "trigger_patterns", trigger
    for definition in [entry.short_definition, entry.long_definition]:
        if definition:
            yield "definitions", definition


def _retrievable(entry: TaxonomyEntry) -> bool:
    if entry.activation_status == ActivationStatus.deprecated.value or entry.academic_status == "deprecated":
        return False
    return bool(entry.enabled_for_retrieval or entry.enabled_for_classification or entry.activation_status == ActivationStatus.active.value)


def _is_healthy_suppressor(entry: TaxonomyEntry) -> bool:
    return bool(entry.healthy_suppressor or entry.canonical_category == "healthy_reasoning_pattern")
