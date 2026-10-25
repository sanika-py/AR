# AwazRakshak UI/UX Specification

Source of truth for implemented product behavior: [BRAIN.md](../../BRAIN.md). This document summarizes the attached UI/UX architecture specification; its proposed interface is **Planned** and is not the current application.

## Status and design intent

The supplied specification describes an emergency-call dashboard intended to act as a cognitive anchor for officers. It calls for a low-fatigue palette, calm hierarchy, no flashing warnings, and human-in-the-loop safeguards. It also proposes multiple capabilities that do not exist in the current Streamlit app. This is a target specification, not evidence that those features or integrations are implemented or approved.

The current app is a single-page live microphone workflow. Emotion scores, derived indicators, and attention categories are advisory; its configured emotion labels are uncalibrated. The multi-call queue and all components/actions below are **Planned** unless identified as current in [BRAIN.md](../../BRAIN.md).

## Planned three-column layout

The specification organizes the dashboard left-to-right from navigation, to queue triage, to focused analysis of one selected call.

| Column | Planned purpose | Components described by the specification |
|---|---|---|
| 1. Global navigation and status sidebar (left) | Navigate product areas and show system connectivity. | Active Dashboard; Analytics & Trends; Case Files; System Diagnostics; status chip for live acoustic-model connectivity and audio-stream integration. |
| 2. Active call prioritization queue (center) | Main workspace for reviewing active calls, sorted by urgency score from 1 to 10. | Call cards with priority color bar, call metadata, recommended insight/protocol, and keyword alert chips. |
| 3. Live audio and emotional analysis (right) | Inspect the currently selected active call. | Live waveform; emotional trajectory; streaming transcript preview; officer observations input for notes, operational tags, and manual overrides. |

The specification asks for no panic-inducing animation or flashing warnings. Queue sorting and panel selection behavior beyond the interaction table below are not specified.

## Planned queue card fields

Each center-column card is described as containing:

- **Priority color bar:** a left border representing urgency tier: Crimson, Orange, Soft Amber, or Sage Green.
- **Call metadata:** call-duration timer, caller identifier/location tag, and assigned handling agent.
- **AI actionable insight:** a prominent recommended protocol for the current conversation state.
- **Keyword alert chips:** triggers extracted from live speech-to-text; examples in the source are “threatened,” “OTP shared,” and “extortion.”

The queue is specified as continuously sorted by urgency scores from 1 to 10. The scoring method, tie-breaking, update cadence, and handling of missing values are unspecified. The current repository has no multi-call queue, speech-to-text, caller/location fields, or assigned-agent data model.

## Planned P1-P4 priority table

The following table transcribes the priority examples from the supplied specification. It is not a validated rubric or executable policy. Its proposed prompts and actions must not be treated as approved system instructions or automatic decisions.

| Priority | Vocal and emotion profile in source | Example “AI Guidance Prompt” in source | Recommended action in source |
|---|---|---|---|
| **P1 - CRITICAL** | High-frequency tremor, severe distress, extreme fear. | “De-escalate tone immediately; assure victim immediate assistance is active.” | Emergency trace, instant bank hotline escalation, freeze order. |
| **P2 - HIGH** | Elevated pitch, rapid speech rate, panic/anger. | “Gather primary transaction hash/account numbers to lock funds.” | Initiate transaction blockage, log victim statement details. |
| **P3 - MODERATE** | Controlled anxiety, hesitation, moderate distress. | “Maintain calm tone; systematically verify caller identity and timeline.” | Draft formal case file, verify caller identity, collect evidence. |
| **P4 - ROUTINE** | Neutral tone, low vocal pitch variability, calm. | “Guide caller through online fraud portal submission process.” | Standard incident reporting, automated ticket creation. |

These four priority bands do not correspond directly to the current application's three provisional attention categories (`Routine`, `Elevated`, `High`). The current app's configured emotion classifier returns seven labels and does not implement the voice profiles, keyword model, or operational action routing described here.

## Planned interactions

| Interaction | System response described by the source | Operational goal stated by the source | Status and safeguard |
|---|---|---|---|
| **Select** a call card | Focus the right panel on that line's live metrics and transcript stream. | Quickly inspect a high-distress caller situation. | **Planned.** No call-card selection or transcript stream exists today. Selection must not imply a decision or validated risk finding. |
| **Escalate** | Notify a supervisor and route the incident to a rapid-response team. | Fast-track financial freeze or dispatch. | **Planned.** Requires integrations, permissions, and an explicit human-controlled workflow; no notifications or external routing exist today. |
| **Flag for Review** | Log an audio snippet and emotion timeline for supervisor audit. | Quality control and model-baseline training. | **Planned in the source, but conflicts with the current no-raw-audio-storage rule.** No snippet retention or training workflow is implemented or approved. |
| **Transfer** the call | Open a quick-transfer modal for specialized-department routing. | Hand off the caller without losing recorded context. | **Planned.** No telephony transfer or department-routing integration exists today. “Recorded context” requires an explicit privacy and retention decision. |

## Named design tokens

The source specifies named color families rather than exact hex values for the proposed queue urgency colors. The neutral theme values below are the existing AwazRakshak calm-theme palette; priority color values remain unspecified by the source.

| Token | Value / source name | Intended use |
|---|---|---|
| `color.canvas` | `#F4F8F8` | Main calm page background. |
| `color.surface.secondary` | `#E3EEEE` | Secondary surfaces and cards. |
| `color.text.primary` | `#24383B` | Primary text. |
| `color.action.primary` | `#4F8F94` | Primary accent/action color in the existing calm theme. |
| `color.border.default` | `#C9DCDC` | Borders and separators. |
| `color.priority.p1` | Crimson (exact value unspecified) | P1 priority bar/badge. |
| `color.priority.p2` | Orange (exact value unspecified) | P2 priority bar/badge. |
| `color.priority.p3` | Soft Amber (exact value unspecified) | P3 priority bar/badge. |
| `color.priority.p4` | Sage Green (exact value unspecified) | P4 priority bar/badge. |
| `motion.alert` | No flashing or panic-inducing animation | Status and urgency feedback should remain calm. |

The exact priority colors, contrast pairs, typography, spacing, focus, hover, disabled, and error tokens are not given in the PDF and need design decisions before implementation.

## Responsible AI directive

The PDF states that AI predictions are decision-support signals and never replace officer discretion or official procedure. The interface must present emotion outputs and priority bands as advisory, keep the officer in control, and avoid implying that a model score establishes a caller's emotional state or determines danger, guilt, deception, dispatch, or operational action. This is consistent with the current project directive in [BRAIN.md](../../BRAIN.md).

The PDF also describes emotion probabilities as generated using “pitch, energy, and spectral acoustic feature models.” The current code uses a pinned wav2vec2 sequence-classification model and does not establish that description; it should not be copied as a verified technical claim without review.

## Questions requiring decisions

1. What exact hex values and accessible contrast requirements should be used for Crimson, Orange, Soft Amber, and Sage Green priority tokens?
2. How should the proposed P1-P4 bands map to (or replace) the current three provisional attention categories, and what reviewed evidence should support any scoring thresholds?
3. What generates the 1-10 urgency score and keyword chips? Is speech-to-text or keyword detection in scope, and what languages and error handling are required?
4. Should “AI actionable insight” display operational recommendations, given the current requirement that model outputs remain advisory and do not direct dispatch or financial action?
5. May “Flag for Review” retain any audio snippet? This conflicts with the current rule that raw audio is never stored; if audio retention remains prohibited, what audio-free review record is acceptable?
6. Which approved systems, roles, and confirmation steps would authorize supervisor notifications, rapid-response routing, account freezes, case-file creation, and transfers?
7. What identifies a call, provides caller/location/agent metadata, and determines queue ordering, tie-breaking, and refresh cadence?
8. Are Analytics & Trends, Case Files, System Diagnostics, waveform, transcript, trajectory chart, and officer observations all in scope for the first frontend release?
9. Should the “recorded context” mentioned for transfers mean transcript/notes only, given the raw-audio retention rule?
10. Is the PDF's description of the model as using pitch, energy, and spectral acoustic feature models technically approved, or should the UI/documentation describe only the verified pinned wav2vec2 classifier?
