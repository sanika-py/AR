# AwazRakshak UI specification

The implemented user interface is the React application in `frontend/`. It uses a three-column dashboard with a navigation/sidebar, queue, and selected-call detail area. Mock data is used by default; live microphone mode is enabled with `VITE_USE_MOCK=false`.

The queue displays synthetic call fields including priority, duration, caller/agent tags, an advisory insight, and keyword chips. The right panel contains waveform and emotional trajectory charts, transcript and notes areas, and demo action controls. Select updates the detail panel. Escalate, Flag for Review, and Transfer currently update only demo UI state.

Design tokens are defined in `frontend/src/styles.css` and use a calm off-white, slate, sage, soft amber, orange, and muted crimson palette. Avoid neon colors, flashing, and panic animation. Keyboard access and sufficient contrast are required.

**Responsible AI directive:** Emotion scores, distress/nervousness, attention categories, and priority/urgency values are advisory and uncalibrated. They are not decisions about danger, deception, guilt, or dispatch. Keep that limitation visible wherever outputs appear.
