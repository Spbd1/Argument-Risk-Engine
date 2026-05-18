from __future__ import annotations

from collections import Counter
from typing import Any

from argument_risk_engine.taxonomy.models import ActivationStatus, TaxonomyPack
from argument_risk_engine.taxonomy.validator import validate_taxonomy_pack_detailed


def coverage_report(pack: TaxonomyPack) -> dict[str, Any]:
    entries = pack.entries
    total = len(entries)
    active = [entry for entry in entries if entry.active]
    return {
        "entry_count": total,
        "active_count": len(active),
        "enabled_for_classification_count": sum(1 for entry in entries if entry.enabled_for_classification),
        "review_required_count": sum(1 for entry in entries if entry.activation_status == ActivationStatus.review_required.value),
        "deprecated_count": sum(1 for entry in entries if entry.activation_status == ActivationStatus.deprecated.value),
        "by_category": dict(sorted(Counter(entry.canonical_category for entry in entries).items())),
        "by_pack": dict(sorted(Counter(entry.pack for entry in entries).items())),
        "by_detection_level": dict(sorted(Counter(entry.detection_level for entry in entries).items())),
        "by_academic_status": dict(sorted(Counter(entry.academic_status for entry in entries).items())),
        "by_activation_status": dict(sorted(Counter(entry.activation_status for entry in entries).items())),
        "missing_examples_count": sum(1 for entry in active if not entry.positive_examples or not entry.negative_examples),
        "missing_false_positive_warnings_count": sum(1 for entry in active if not entry.common_false_positives),
    }


def audit_pack(pack: TaxonomyPack) -> dict[str, Any]:
    report = validate_taxonomy_pack_detailed(pack)
    coverage = coverage_report(pack)
    return {
        "ok": report.ok,
        "entry_count": report.entry_count,
        "active_classification_count": report.active_classification_count,
        "error_count": len(report.errors),
        "warning_count": len(report.warnings),
        "errors": [issue.to_dict() for issue in report.errors],
        "warnings": [issue.to_dict() for issue in report.warnings],
        "coverage": coverage,
    }
