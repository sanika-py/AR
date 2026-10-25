# Prompt and User-Facing Language

Source of truth: [BRAIN.md](BRAIN.md).

## Current system

The current runtime has no language model, prompt template, speech-to-text component, or prompt-driven inference. The pinned classifier consumes audio and returns seven configured labels. Its scores are uncalibrated. `app.py` supplies fixed UI text and labels derived indicators and attention categories as indicative.

## Current wording principles

- Call the emotion outputs model scores or raw model labels.
- Label distress and nervousness as “Derived indicator (not a model class)”.
- Describe Routine, Elevated, and High as indicative attention categories using provisional thresholds.
- Keep the visible disclaimer: “Indicative signals to support the officer's judgement. Not a decision about danger, deception, guilt or dispatch.”
- Do not state that a score proves a person's feelings, truthfulness, risk, or intent.

## Planned copy review

**Planned:** Review accessible UI wording, uncertainty descriptions, quality warnings, consent language, and translations with intended users and relevant domain reviewers. There is no LLM prompt library to configure today; adding prompt-driven generation would require separate design and evaluation.
