# Evaluation Protocol

The evaluation harness is a practical regression tool. It is not a claim of scientific, clinical, legal, or moderation validity.

## Running evaluation

```bash
make evaluate
```

or:

```bash
python scripts/run_evaluation.py --json
```

The default dataset is `data/benchmarks/mini_eval_set.jsonl`.

## Dataset format

Each JSONL row should include:

```json
{
  "id": "case_001",
  "text": "Example text.",
  "gold_labels": ["overgeneralization"],
  "gold_evidence_spans": ["Everyone"],
  "difficulty": "easy",
  "notes": "Why this belongs in the benchmark."
}
```

Use an empty `gold_labels` array for negatives and hard negatives.

## Metrics

The runner computes lightweight label metrics and error buckets:

- false positives
- false negatives
- evidence-span misses
- aggregate benchmark counts

Treat these as engineering QA indicators only.

## Review workflow

1. Run evaluation before and after taxonomy or classifier changes.
2. Inspect false positives first to ensure the system remains conservative.
3. Inspect false negatives to identify missing taxonomy signals or overly strict rules.
4. Inspect evidence-span misses for explanation quality.
5. Update hard negatives when new false-positive patterns appear.

## Acceptance threshold

For the MVP, the benchmark should run reliably and expose errors clearly. Do not optimize solely for score by making aggressive labels; conservative behavior with transparent misses is preferable to over-classification.
