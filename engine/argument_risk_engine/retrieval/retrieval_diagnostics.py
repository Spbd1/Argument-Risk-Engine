from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievalDiagnostics:
    query_terms: list[str] = field(default_factory=list)
    considered_entry_count: int = 0
    raw_candidate_count: int = 0
    returned_candidate_count: int = 0
    suppressed_candidate_count: int = 0
    healthy_suppressor_count: int = 0
    ignored_terms: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def diagnostics(matches: list[object]) -> dict[str, int]:
    return {"candidate_count": len(matches)}
