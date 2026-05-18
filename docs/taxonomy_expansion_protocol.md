# Taxonomy Expansion Protocol

Use this protocol when proposing, importing, or activating new taxonomy entries.

## 1. Propose

Create or import candidate entries with clear names, definitions, signals, examples, and false-positive notes. New entries should default to a non-aggressive status such as draft or review-required until reviewed.

## 2. Review evidence requirements

For each candidate, define the minimum textual evidence required. If the risk cannot be detected from the submitted text without substantial context, mark it as requiring human judgment and avoid enabling deterministic classification until safeguards exist.

## 3. Add examples

Add at least:

- Two positive examples.
- Two negative examples.
- Two hard negatives that contain similar words but should not be classified.

Avoid examples that are political, medical-diagnostic, offensive, or personally targeted.

## 4. Validate

Run the taxonomy validator from the dashboard or CLI. Fix missing IDs, duplicate IDs, unsupported enum values, and entries without evidence requirements.

## 5. Benchmark

Add representative examples to a benchmark file and run:

```bash
make evaluate
```

Metrics are engineering signals only. Manually inspect false positives and false negatives before activation.

## 6. Activate conservatively

Only set `enabled_for_classification` and active status when evidence requirements, examples, and false-positive controls are sufficient. Prefer review-required status for uncertain entries.

## 7. Document changes

Update docs, changelog notes, and dashboard guidance when taxonomy semantics or workbook schemas change.
