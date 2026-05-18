# Limitations

Argument-Risk-Engine is a human-review aid, not an automated decision system.

## Required limitations

- May produce false positives.
- May miss subtle risks.
- Should not be used for automated moderation.
- Does not judge intent.
- Does not determine factual truth.
- Does not diagnose bias in a person.
- Human review is required for high-stakes use.
- Large taxonomy does not mean complete taxonomy.
- Large taxonomy does not mean aggressive classification.

## Practical implications

A finding means only that the system identified a taxonomy-grounded pattern with some textual support. It does not mean the author is malicious, the claim is false, or action should be taken. A non-finding does not mean the text is safe, accurate, unbiased, or complete.

## MVP constraints

- The deterministic baseline is lexical and can miss paraphrases.
- Context outside the submitted text is not reliably available.
- Evaluation data is intentionally small and demo-oriented.
- File-based storage is convenient locally but not a multi-user production architecture.
- External model providers, if configured, may introduce cost, latency, privacy, and reliability concerns.

## High-stakes use

For employment, education, finance, housing, legal, health, safety, public-benefit, or moderation workflows, outputs must be reviewed by qualified humans under an appropriate policy. The MVP should not be connected directly to enforcement actions.
