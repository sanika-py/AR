# Prompt and User-Facing Language

Source of truth: [BRAIN.md](BRAIN.md).

## Current system

The current runtime has no generative language model or prompt-driven inference. The pinned classifier consumes audio and returns seven configured labels with uncalibrated scores. Optional local faster-whisper ASR can produce partial text when explicitly enabled and a local model is provided. `app.py` supplies fixed UI text and labels derived indicators and attention categories as indicative.

## Current wording principles

- Call the emotion outputs model scores or raw model labels.
- Label distress and nervousness as “Derived indicator (not a model class)”.
- Describe Routine, Elevated, and High as indicative attention categories using provisional thresholds.
- Keep the visible disclaimer: “Indicative signals to support the officer's judgement. Not a decision about danger, deception, guilt or dispatch.”
- Do not state that a score proves a person's feelings, truthfulness, risk, or intent.

## Planned copy review

**Planned:** Review accessible UI wording, uncertainty descriptions, quality warnings, consent language, and translations with intended users and relevant domain reviewers. There is no LLM prompt library to configure today; adding prompt-driven generation would require separate design and evaluation.

## Approved advisory priority templates

The following fixed strings are approved for the deterministic provisional priority feature. They are not generated from audio and do not recommend dispatch or another operational decision:

- **P1:** “Advisory: Consider careful follow-up with calm, open-ended questions and apply established procedures.”
- **P2:** “Advisory: Consider clarifying the caller's account with calm, open-ended questions.”
- **P3:** “Advisory: Consider reviewing the conversation context and following standard intake steps.”
- **P4:** “Advisory: Continue standard intake and use your judgement in context.”
