# Taxonomy Design

The taxonomy is the control surface for Argument-Risk-Engine. The engine should only emit labels that exist in active taxonomy entries and are supported by evidence in the submitted text.

## Design principles

- **Taxonomy-first:** every finding maps to a taxonomy entry.
- **Evidence-grounded:** every finding should include a specific text span when possible.
- **Conservative activation:** entries can exist for research or review without being enabled for classification.
- **False-positive aware:** each entry should document common legitimate uses that should not be classified.
- **Human-review oriented:** output is meant to support review, not replace judgment.

## Entry fields

Important entry concepts include:

- `id`: stable machine identifier.
- `name`: human-readable label.
- `canonical_category`: broad category for filtering and reports.
- `short_definition` and `long_definition`: reviewer-facing meaning.
- `signals` and `trigger_patterns`: retrieval/classification hints.
- `minimum_evidence_requirement`: required evidence before classification.
- `positive_examples` and `negative_examples`: examples for calibration.
- `common_false_positives` and `exclusion_criteria`: safeguards.
- `enabled_for_retrieval`: whether the retriever can surface the entry.
- `enabled_for_classification`: whether a classifier may emit the entry.
- `activation_status`: active, draft, deprecated, or review-required state.
- `requires_human_judgment`: escalates findings for careful review.

## Activation model

A large taxonomy can include many inactive, draft, or review-required entries. This does not mean the engine should classify aggressively. For MVP analysis, only active classification-enabled entries should produce findings.

## Healthy reasoning patterns

Healthy or mitigating patterns may reduce or suppress risky classifications. Examples include explicit uncertainty, balanced comparison, narrow scope, cited evidence, or acknowledged exceptions.

## Import/export

The dashboard and CLI support user-managed Excel workbooks. The real living workbook should be stored outside Git or under ignored local import directories. Exported workbooks are local artifacts for review and sharing.

## Quality expectations

Before enabling an entry for classification, contributors should verify:

1. The definition is clear.
2. The evidence requirement is concrete.
3. Examples include positives and hard negatives.
4. False-positive guards are documented.
5. Severity guidance is not exaggerated.
6. The entry can be explained to a human reviewer.
