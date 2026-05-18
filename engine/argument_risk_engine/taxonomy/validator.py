from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from argument_risk_engine.taxonomy.models import (
    AcademicStatus,
    ActivationStatus,
    CanonicalCategory,
    FalsePositiveSensitivity,
    TaxonomyPack,
)


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    entry_id: str | None = None
    row_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class TaxonomyValidationReport:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    entry_count: int = 0
    active_classification_count: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, issue: ValidationIssue) -> None:
        if issue.severity == "warning":
            self.warnings.append(issue)
        else:
            self.errors.append(issue)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "entry_count": self.entry_count,
            "active_classification_count": self.active_classification_count,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


def _issue(code: str, message: str, entry: object | None = None, severity: str = "error") -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity=severity,
        entry_id=getattr(entry, "id", None),
        row_number=getattr(entry, "row_number", None),
    )


def validate_taxonomy_pack_detailed(pack: TaxonomyPack) -> TaxonomyValidationReport:
    report = TaxonomyValidationReport(entry_count=len(pack.entries))
    seen: dict[str, int | None] = {}
    for entry in pack.entries:
        if entry.id in seen:
            report.add(_issue("duplicate_id", f"duplicate id: {entry.id}", entry))
        seen[entry.id] = entry.row_number
        for field_name, raw_value in dict(entry.metadata.get("invalid_enums", {})).items():
            report.add(_issue("invalid_enum", f"{entry.id} has invalid {field_name}: {raw_value}", entry))

        active_for_classification = entry.enabled_for_classification and entry.activation_status == ActivationStatus.active.value
        if active_for_classification:
            report.active_classification_count += 1

        if entry.academic_status == AcademicStatus.canonical.value and not entry.source_refs:
            report.add(_issue("canonical_missing_source_refs", f"{entry.id} is canonical but has no source_refs", entry))
        if active_for_classification:
            if not entry.positive_examples:
                report.add(_issue("active_missing_positive_examples", f"{entry.id} is active for classification but has no positive examples", entry))
            if not entry.negative_examples:
                report.add(_issue("active_missing_negative_examples", f"{entry.id} is active for classification but has no negative examples", entry))
            if not entry.minimum_evidence_requirement:
                report.add(_issue("active_missing_minimum_evidence", f"{entry.id} is active for classification but has no minimum evidence requirement", entry))
            if not entry.common_false_positives:
                report.add(_issue("active_missing_false_positive_warnings", f"{entry.id} is active for classification but has no false-positive warnings", entry))
        if entry.canonical_category == CanonicalCategory.healthy_reasoning_pattern.value and entry.enabled_for_classification:
            report.add(_issue("healthy_classification_disabled", f"{entry.id} is a healthy reasoning pattern and must not be returned as a risk", entry))
        if entry.activation_status == ActivationStatus.deprecated.value and entry.enabled_for_classification:
            report.add(_issue("deprecated_active", f"{entry.id} is deprecated but enabled for classification", entry))
        if entry.activation_status == ActivationStatus.backlog.value and entry.enabled_for_classification:
            report.add(_issue("backlog_classification", f"{entry.id} is backlog but enabled for classification", entry))
        if (
            entry.false_positive_sensitivity == FalsePositiveSensitivity.high.value
            and entry.activation_status == ActivationStatus.active.value
            and "import_as_active" not in str(entry.metadata.get("codex_import_action", ""))
        ):
            report.add(_issue("high_fp_active", f"{entry.id} has high false-positive sensitivity and should normally remain review_required", entry, severity="warning"))
        if entry.academic_status == AcademicStatus.operational.value and entry.academic_consensus != "operational_only":
            report.add(_issue("operational_presented_academic", f"{entry.id} is operational and must not be presented as an academic construct", entry, severity="warning"))
    return report


def validate_taxonomy_pack(pack: TaxonomyPack) -> list[str]:
    report = validate_taxonomy_pack_detailed(pack)
    return [issue.message for issue in report.errors + report.warnings]
