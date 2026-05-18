# Annotation Guidelines

These guidelines describe how to create and review examples for the mini benchmark and taxonomy entries.

## Reviewer stance

Annotate argument-level patterns, not people. Do not infer author intent, moral character, factual truth, medical status, or political legitimacy. Mark only what is supported by the text.

## Labeling rules

- Use a label only when the text meets the taxonomy entry’s minimum evidence requirement.
- Include exact evidence spans when a label is present.
- Prefer no label when the example is ambiguous or depends on missing context.
- Use hard negatives for texts that contain trigger words in legitimate or literal ways.
- Keep notes short and practical.

## Example categories

- **Positive:** the target risk is present and evidence is clear.
- **Negative:** no taxonomy risk is expected.
- **Hard negative:** wording resembles a risk pattern, but context should prevent classification.

## Evidence spans

Evidence spans should be short, exact substrings from the input. If no exact span can be selected, the example may be unsuitable for deterministic evaluation.

## Content constraints

For this open-source demo set, avoid:

- Political examples.
- Medical diagnosis examples.
- Offensive examples.
- Personal attacks against real people.
- Protected-class targeting.
- Instructions for wrongdoing.

## Adjudication

When reviewers disagree, record the disagreement and keep the example out of strict evaluation until resolved. The preferred resolution is usually a narrower taxonomy definition or a new hard negative.
