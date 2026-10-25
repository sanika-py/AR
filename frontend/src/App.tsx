import { useEffect, useMemo, useState } from "react";
import { LiveWaveform, MockWaveform, TrajectoryChart } from "./Charts";
import { formatDuration, generateMockCalls } from "./mockData";
import type { MockCall } from "./mockData";
import { useAnalysisStore } from "./store";
import { useLiveAudio } from "./useLiveAudio";

const navItems = [
  "Dashboard",
  "Analytics & Trends",
  "Case Files",
  "System Diagnostics",
];
const priorityColor = {
  P1: "bg-priority-p1",
  P2: "bg-priority-p2",
  P3: "bg-priority-p3",
  P4: "bg-priority-p4",
};
const categoryColor = {
  Routine: "bg-sage",
  Elevated: "bg-soft-amber",
  High: "bg-muted-crimson",
};
const priorityStyle = {
  P1: "border-priority-p1 bg-priority-p1/10 text-[#743c37]",
  P2: "border-priority-p2 bg-priority-p2/15 text-[#71401f]",
  P3: "border-priority-p3 bg-priority-p3/25 text-[#66501f]",
  P4: "border-priority-p4 bg-priority-p4/25 text-[#345849]",
};
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const idleCall: MockCall = {
  id: "no-session",
  durationSeconds: 0,
  caller: "No active call",
  location: "Waiting for a live session",
  agent: "—",
  insight: "No analysis event received yet.",
  keywords: [],
  transcript: [],
  distress: [0],
  nervousness: [0],
  waveformSeed: 0,
  notes: "",
};

function statusLabel(status: ReturnType<typeof useLiveAudio>["status"]): string {
  const labels = {
    idle: "Not recording",
    requesting: "Requesting microphone permission",
    connecting: "Connecting to local analysis service",
    listening: "Listening",
    reconnecting: "Reconnecting to local analysis service",
    error: "Analysis unavailable",
  };
  return labels[status];
}

function App() {
  const [tick, setTick] = useState(0);
  const [selectedId, setSelectedId] = useState("AR-2048");
  const [consent, setConsent] = useState(false);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [flagged, setFlagged] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [transferOpen, setTransferOpen] = useState(false);
  const [department, setDepartment] = useState("Financial fraud");
  const latest = useAnalysisStore((state) => state.latest);
  const transcript = useAnalysisStore((state) => state.transcript);
  const history = useAnalysisStore((state) => state.history);
  const live = useLiveAudio(!USE_MOCK);
  useEffect(() => {
    if (!USE_MOCK) return;
    const timer = window.setInterval(() => setTick((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const mockCalls = useMemo(() => (USE_MOCK ? generateMockCalls(tick) : []), [tick]);
  const liveCall: MockCall = {
    id: live.sessionId ?? "live-session",
    durationSeconds: latest?.elapsed ?? 0,
    caller: "Live microphone session",
    location: "Browser microphone",
    agent: "Local operator",
    insight: latest
      ? "Top raw model label: " +
        latest.scores.reduce((top, score) => (score.score > top.score ? score : top))
          .label +
        " · Advisory"
      : "Waiting for the first analysis event.",
    keywords: [],
    transcript: [],
    distress: history.length
      ? history.map((event) => event.indicators.distress_indicator)
      : [0],
    nervousness: history.length
      ? history.map((event) => event.indicators.nervousness_indicator)
      : [0],
    waveformSeed: history.length,
    notes: "",
    category: latest?.category,
  };
  const calls = USE_MOCK ? mockCalls : live.sessionActive ? [liveCall] : [];
  const selected = USE_MOCK
    ? (calls.find((call) => call.id === selectedId) ?? calls[0] ?? idleCall)
    : live.sessionActive
      ? liveCall
      : idleCall;

  return (
    <div className="min-h-screen bg-canvas text-slate">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-surface px-5 py-4 lg:px-7">
        <div className="flex items-center gap-3">
          <div
            aria-hidden="true"
            className="grid h-10 w-10 place-items-center rounded-xl bg-teal-strong text-sm font-bold text-white"
          >
            AR
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-teal-strong">
              Officer workspace
            </p>
            <h1 className="text-xl font-semibold">AwazRakshak</h1>
          </div>
        </div>
        <span
          className="flex items-center gap-2 rounded-full border border-line bg-white px-3 py-2 text-xs font-semibold"
          role="status"
          aria-label={
            USE_MOCK
              ? "Mock events active; backend not connected"
              : "Live recording status: " + live.status
          }
        >
          <i aria-hidden="true" className="h-2.5 w-2.5 rounded-full bg-priority-p4" />
          {USE_MOCK ? "Mock events active" : statusLabel(live.status)}
          <span className="font-normal text-slate-muted">
            · {USE_MOCK ? "Backend not connected" : "Local analysis service"}
          </span>
        </span>
      </header>
      <div className="mx-auto grid min-h-[calc(100vh-73px)] max-w-[1920px] grid-cols-1 lg:grid-cols-[220px_minmax(330px,420px)_minmax(480px,1fr)] xl:grid-cols-[236px_minmax(360px,440px)_minmax(560px,1fr)]">
        <aside className="border-b border-line bg-surface p-4 lg:border-b-0 lg:border-r">
          <p className="px-3 py-2 text-[11px] font-bold uppercase tracking-[.15em] text-slate-muted">
            Workspace
          </p>
          <nav aria-label="Main navigation" className="space-y-1">
            {navItems.map((item, i) => (
              <button
                key={item}
                type="button"
                aria-current={i === 0 ? "page" : undefined}
                disabled={i > 0}
                className={
                  "flex min-h-11 w-full items-center justify-between rounded-xl px-3 text-left text-sm font-medium " +
                  (i === 0
                    ? "bg-white text-slate shadow-sm"
                    : "text-slate-muted opacity-80")
                }
              >
                {item}
                {i > 0 && (
                  <span className="text-[10px] font-semibold uppercase tracking-wide">
                    Planned
                  </span>
                )}
              </button>
            ))}
          </nav>
          <section
            className="mt-7 rounded-2xl border border-line bg-white p-4"
            aria-labelledby="model-heading"
          >
            <h2
              id="model-heading"
              className="text-xs font-bold uppercase tracking-[.12em] text-slate-muted"
            >
              Model status
            </h2>
            <p className="mt-3 flex items-center gap-2 text-sm font-semibold">
              <i
                aria-hidden="true"
                className={
                  "h-2.5 w-2.5 rounded-full " +
                  (USE_MOCK || live.status === "listening"
                    ? "bg-priority-p4"
                    : live.status === "error"
                      ? "bg-muted-crimson"
                      : "bg-priority-p3")
                }
              />
              {USE_MOCK
                ? "Mock model status"
                : live.status === "listening"
                  ? "Local analysis connected"
                  : live.status === "error"
                    ? "Analysis unavailable"
                    : "Local analysis " + live.status}
            </p>
            <p className="mt-2 text-xs leading-5 text-slate-muted">
              {USE_MOCK
                ? "Demo data only. No model or live audio connection."
                : "Pinned local model status follows the analysis service connection."}
            </p>
          </section>
          <section
            className="mt-4 rounded-2xl border border-line bg-white p-4"
            aria-labelledby="recording-heading"
          >
            <h2
              id="recording-heading"
              className="text-xs font-bold uppercase tracking-[.12em] text-slate-muted"
            >
              Recording consent
            </h2>
            <label className="mt-3 flex cursor-pointer items-start gap-2 text-sm leading-5">
              <input
                type="checkbox"
                checked={consent}
                onChange={(event) => {
                  const authorised = event.target.checked;
                  setConsent(authorised);
                  if (!authorised && live.recording) void live.stop();
                }}
                className="mt-1 h-4 w-4 accent-teal-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-strong"
              />
              <span>I am authorised to record this call.</span>
            </label>
            {USE_MOCK ? (
              <p className="mt-3 text-xs leading-5 text-slate-muted">
                Mock mode is on. No microphone is accessed. Set{" "}
                <code>VITE_USE_MOCK=false</code> for live audio.
              </p>
            ) : (
              <>
                <div className="mt-3 flex flex-wrap gap-2">
                  {!live.recording ? (
                    <button
                      type="button"
                      onClick={() => void live.start()}
                      disabled={!consent}
                      className="min-h-11 rounded-xl bg-teal-strong px-3 text-xs font-semibold text-white enabled:hover:bg-[#2e6065] disabled:cursor-not-allowed disabled:opacity-55"
                    >
                      {live.status === "requesting"
                        ? "Requesting microphone…"
                        : "Start call recording"}
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => void live.stop()}
                      className="min-h-11 rounded-xl border border-line bg-canvas px-3 text-xs font-semibold hover:bg-surface"
                    >
                      Stop recording
                    </button>
                  )}
                </div>
                <p role="status" className="mt-3 text-xs font-medium">
                  {live.error || statusLabel(live.status)}
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-muted">
                  Observed analysis latency:{" "}
                  {live.latencyMs === null ? "—" : live.latencyMs + " ms"}
                </p>
              </>
            )}
          </section>
          {USE_MOCK && (
            <section
              className="mt-5 rounded-2xl border border-line bg-white p-4"
              aria-label="Priority legend"
            >
              <h2 className="text-xs font-bold uppercase tracking-[.12em] text-slate-muted">
                Priority bands · Advisory
              </h2>
              <ul className="mt-3 space-y-2 text-xs">
                {(["P1", "P2", "P3", "P4"] as const).map((p) => (
                  <li key={p} className="flex items-center gap-2">
                    <i
                      aria-hidden="true"
                      className={"h-3 w-3 rounded-sm " + priorityColor[p]}
                    />
                    <strong>{p}</strong>
                    <span className="text-slate-muted">
                      {{ P1: "Crimson", P2: "Orange", P3: "Soft amber", P4: "Sage" }[p]}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}
          <p className="mt-6 rounded-xl bg-canvas p-3 text-xs leading-5 text-slate-muted">
            Indicative signals to support officer judgement. Not a determination or
            operational instruction.
          </p>
        </aside>
        <main
          className="border-b border-line p-4 sm:p-5 lg:border-b-0 lg:border-r lg:p-6"
          aria-labelledby="queue-heading"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.12em] text-slate-muted">
                {USE_MOCK ? "Live triage · Mock queue" : "Live triage · Local session"}
              </p>
              <h2 id="queue-heading" className="mt-1 text-xl font-semibold">
                Active calls
              </h2>
            </div>
            <span className="rounded-full border border-line bg-white px-2.5 py-1.5 text-xs font-semibold">
              {USE_MOCK
                ? calls.length + " demo calls"
                : calls.length + " live sessions"}
            </span>
          </div>
          <p className="mb-4 mt-2 text-xs leading-5 text-slate-muted">
            {USE_MOCK
              ? "Sorted by mock urgency score (1–10), highest first. All AI signals are advisory."
              : "This view shows the current microphone session only. Analysis outputs are advisory."}
          </p>
          <div
            className="space-y-3"
            role="group"
            aria-label={
              USE_MOCK
                ? "Mock call queue sorted by urgency score"
                : "Live microphone session"
            }
          >
            {!USE_MOCK && calls.length === 0 && (
              <p className="rounded-xl border border-dashed border-line bg-white p-4 text-sm leading-6 text-slate-muted">
                Authorise recording and select Start call recording to begin a local
                session.
              </p>
            )}
            {calls.map((call) => (
              <button
                key={call.id}
                type="button"
                aria-pressed={call.id === selected.id}
                onClick={() => {
                  setSelectedId(call.id);
                  setMessage("");
                }}
                className={
                  "group relative block min-h-40 w-full overflow-hidden rounded-2xl border bg-white p-4 pl-5 text-left shadow-sm hover:border-teal focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal " +
                  (call.id === selected.id
                    ? "border-teal ring-2 ring-teal/25"
                    : "border-line")
                }
              >
                <i
                  aria-hidden="true"
                  className={
                    "absolute inset-y-0 left-0 w-1.5 " +
                    (call.priority
                      ? priorityColor[call.priority]
                      : call.category
                        ? categoryColor[call.category]
                        : "bg-teal")
                  }
                />
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold">
                      {call.caller}
                      <span className="ml-2 text-xs font-normal text-slate-muted">
                        {call.id}
                      </span>
                    </p>
                    <p className="mt-1 text-xs text-slate-muted">{call.location}</p>
                  </div>
                  <span
                    className={
                      "shrink-0 rounded-full border px-2 py-1 text-[11px] font-bold " +
                      (call.priority
                        ? priorityStyle[call.priority]
                        : "border-line bg-canvas text-slate")
                    }
                  >
                    {call.priority
                      ? call.priority + " · Advisory"
                      : call.category
                        ? call.category + " · Advisory"
                        : "Awaiting analysis"}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-muted">
                  <span>
                    {call.urgency !== undefined ? (
                      <>
                        <strong className="text-slate">
                          {call.urgency.toFixed(1)}
                        </strong>
                        /10 urgency · Advisory
                      </>
                    ) : call.category ? (
                      <>{call.category} attention · Advisory</>
                    ) : (
                      "Analysis pending"
                    )}
                  </span>
                  <span className="font-mono tabular-nums">
                    {formatDuration(call.durationSeconds)}
                  </span>
                  <span>Agent {call.agent}</span>
                </div>
                <p className="mt-3 text-xs leading-5 text-slate">
                  AI insight · Advisory:{" "}
                  {call.insight.replace(/^Advisory signal: /, "")}
                </p>
                <div
                  className="mt-3 flex flex-wrap gap-1.5"
                  aria-label="Mock keyword chips; advisory only"
                >
                  {call.keywords.map((word) => (
                    <span
                      key={word}
                      className="rounded-md bg-surface px-2 py-1 text-[11px] font-medium"
                    >
                      {word}
                    </span>
                  ))}
                  <span className="text-[10px] font-semibold text-slate-muted">
                    Keywords · Advisory
                  </span>
                </div>
                {flagged.includes(call.id) && (
                  <span className="absolute bottom-3 right-3 rounded-md bg-canvas px-2 py-1 text-[10px] font-semibold">
                    Flagged for review
                  </span>
                )}
              </button>
            ))}
          </div>
        </main>
        <section className="min-w-0 p-4 sm:p-5 lg:p-6" aria-labelledby="detail-heading">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.12em] text-slate-muted">
                {USE_MOCK ? "Selected call · Demo" : "Selected call · Local microphone"}
              </p>
              <h2 id="detail-heading" className="mt-1 text-xl font-semibold">
                {selected.caller}
              </h2>
              <p className="mt-1 text-xs text-slate-muted">
                {selected.id} · {selected.location} · Agent {selected.agent}
              </p>
            </div>
            <span
              className={
                "rounded-full border px-3 py-1.5 text-xs font-bold " +
                (selected.priority
                  ? priorityStyle[selected.priority]
                  : "border-line bg-canvas text-slate")
              }
            >
              {selected.priority
                ? selected.priority + " · Advisory"
                : selected.category
                  ? selected.category + " · Advisory"
                  : "Awaiting analysis"}
            </span>
          </div>
          {!USE_MOCK && latest && (
            <section className="mt-4 rounded-2xl border border-line bg-white p-4" aria-label="Live priority rationale, advisory">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <strong>{latest.priority} · {latest.urgency_score}/10 urgency · Advisory</strong>
                <span className="text-xs text-slate-muted">Provisional priority</span>
              </div>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                {latest.priority_reasons.map((reason, index) => (
                  <li key={`${index}-${reason}`}>{reason}</li>
                ))}
              </ul>
              <p className="mt-2 text-sm">{latest.priority_guidance}</p>
            </section>
          )}
          <div className="mt-5 grid gap-4 xl:grid-cols-2">
            <section
              className="min-w-0 rounded-2xl border border-line bg-white p-4"
              aria-labelledby="waveform-heading"
            >
              <div className="flex items-center justify-between gap-2">
                <h3 id="waveform-heading" className="font-semibold">
                  Waveform
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wide text-teal-strong">
                  {USE_MOCK ? "Mock · Advisory" : "Live · Advisory"}
                </span>
              </div>
              <div className="mt-2 rounded-xl bg-canvas px-2">
                {USE_MOCK ? (
                  <MockWaveform seed={selected.waveformSeed} />
                ) : (
                  <LiveWaveform samples={live.waveform} />
                )}
              </div>
              <p className="mt-2 text-xs text-slate-muted">
                {USE_MOCK
                  ? "Synthetic visual only. No microphone is accessed."
                  : "Waveform rendered locally from short in-memory chunks. Raw audio is not saved."}
              </p>
            </section>
            <section
              className="min-w-0 rounded-2xl border border-line bg-white p-4"
              aria-labelledby="trajectory-heading"
            >
              <div className="flex items-center justify-between gap-2">
                <h3 id="trajectory-heading" className="font-semibold">
                  Emotional trajectory
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wide text-teal-strong">
                  Advisory
                </span>
              </div>
              <div className="mt-2">
                <TrajectoryChart call={selected} />
              </div>
              <p className="mt-1 text-xs text-slate-muted">
                {USE_MOCK
                  ? "Mock values · Uncalibrated signals, not a decision."
                  : "Backend values · Uncalibrated signals, not a decision."}
              </p>
            </section>
          </div>
          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            <section
              className="rounded-2xl border border-line bg-white p-4"
              aria-labelledby="transcript-heading"
            >
              <div className="flex items-center justify-between">
                <h3 id="transcript-heading" className="font-semibold">
                  Transcript
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wide text-teal-strong">
                  {USE_MOCK ? "Mock · Advisory" : live.asrEnabled ? "Local ASR · Advisory" : "ASR disabled"}
                </span>
              </div>
              {!USE_MOCK && transcript?.status === "error" ? (
                <p role="status" className="mt-3 rounded-xl bg-canvas px-3 py-2 text-sm leading-6 text-slate-muted">
                  {transcript.message}
                </p>
              ) : !USE_MOCK && live.asrEnabled && transcript?.text ? (
                <div className="mt-3 rounded-xl bg-canvas px-3 py-2 text-sm leading-6">
                  <p>{transcript.text}</p>
                  <p className="mt-2 text-xs text-slate-muted">
                    Partial transcript · {transcript.language ?? "language not detected"} · Advisory
                  </p>
                  {transcript.keyword_hits.length > 0 && (
                    <p className="mt-1 text-xs">Keyword matches · Advisory: {transcript.keyword_hits.join(", ")}</p>
                  )}
                  <button
                    type="button"
                    className="mt-3 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold focus-visible:outline-2 focus-visible:outline-teal"
                    onClick={() => setNotes((current) => ({
                      ...current,
                      [selected.id]: `${current[selected.id] ?? selected.notes}${current[selected.id] ?? selected.notes ? "\n" : ""}${transcript.text}`,
                    }))}
                  >
                    Save transcript to officer note
                  </button>
                </div>
              ) : selected.transcript.length ? (
                <ul className="mt-3 space-y-3 text-sm leading-6">
                  {selected.transcript.map((line) => (
                    <li key={line} className="rounded-xl bg-canvas px-3 py-2">
                      {line}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-3 rounded-xl bg-canvas px-3 py-2 text-sm leading-6 text-slate-muted">
                  Transcript is not available from the current API.
                </p>
              )}
              <p className="mt-2 text-xs text-slate-muted">
                {USE_MOCK
                  ? "Illustrative text. Not connected to speech recognition."
                  : live.asrEnabled
                    ? "Partial ASR is processed locally; transcripts stay in memory unless you save one to an officer note."
                    : "ASR is disabled. No transcript data is produced."}
              </p>
            </section>
            <section
              className="rounded-2xl border border-line bg-white p-4"
              aria-labelledby="notes-heading"
            >
              <div className="flex items-center justify-between">
                <h3 id="notes-heading" className="font-semibold">
                  Officer notes
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wide text-slate-muted">
                  Local demo state
                </span>
              </div>
              <label htmlFor="officer-notes" className="sr-only">
                Officer notes for {selected.id}
              </label>
              <textarea
                id="officer-notes"
                value={notes[selected.id] ?? selected.notes}
                onChange={(event) =>
                  setNotes((current) => ({
                    ...current,
                    [selected.id]: event.target.value,
                  }))
                }
                rows={5}
                placeholder="Add an observation for this demo call…"
                className="mt-3 w-full resize-y rounded-xl border border-line bg-canvas p-3 text-sm leading-6 placeholder:text-slate-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal"
              />
              <p className="mt-2 text-xs text-slate-muted">
                Notes remain in this browser session only.
              </p>
            </section>
          </div>
          <section
            className="mt-4 rounded-2xl border border-line bg-white p-4"
            aria-label="Officer actions"
          >
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() =>
                  setMessage("Escalate is a demo only. No operational action was sent.")
                }
                className="min-h-11 rounded-xl bg-teal-strong px-4 text-sm font-semibold text-white hover:bg-[#2e6065]"
              >
                Escalate
              </button>
              <button
                type="button"
                aria-pressed={flagged.includes(selected.id)}
                onClick={() =>
                  setFlagged((current) =>
                    current.includes(selected.id)
                      ? current.filter((id) => id !== selected.id)
                      : [...current, selected.id],
                  )
                }
                className="min-h-11 rounded-xl border border-line bg-canvas px-4 text-sm font-semibold hover:bg-surface"
              >
                {flagged.includes(selected.id) ? "Unflag review" : "Flag for Review"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setTransferOpen(true);
                  setMessage("");
                }}
                className="min-h-11 rounded-xl border border-line bg-canvas px-4 text-sm font-semibold hover:bg-surface"
              >
                Transfer
              </button>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-muted">
              Demo controls only. Escalation and transfer do not contact services;
              review flags are not saved.
            </p>
            {message && (
              <p role="status" className="mt-3 rounded-lg bg-surface px-3 py-2 text-sm">
                {message}
              </p>
            )}
          </section>
        </section>
      </div>
      {transferOpen && (
        <div className="fixed inset-0 z-10 grid place-items-center bg-slate/40 p-4">
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="transfer-heading"
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                event.preventDefault();
                setTransferOpen(false);
              }
              if (event.key === "Tab") {
                const focusable = Array.from(
                  event.currentTarget.querySelectorAll<HTMLElement>(
                    'button, select, [href], input, textarea, [tabindex]:not([tabindex="-1"])',
                  ),
                );
                const first = focusable[0];
                const last = focusable[focusable.length - 1];
                if (event.shiftKey && document.activeElement === first) {
                  event.preventDefault();
                  last?.focus();
                } else if (!event.shiftKey && document.activeElement === last) {
                  event.preventDefault();
                  first?.focus();
                }
              }
            }}
            className="w-full max-w-md rounded-2xl border border-line bg-white p-5 shadow-xl"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 id="transfer-heading" className="text-lg font-semibold">
                  Transfer · Demo
                </h2>
                <p className="mt-1 text-sm text-slate-muted">
                  Choose a mock team. No call will be routed.
                </p>
              </div>
              <button
                type="button"
                aria-label="Close transfer dialog"
                onClick={() => setTransferOpen(false)}
                className="grid h-10 w-10 place-items-center rounded-lg border border-line text-lg hover:bg-canvas"
              >
                ×
              </button>
            </div>
            <label
              htmlFor="transfer-department"
              className="mt-5 block text-sm font-medium"
            >
              Department
            </label>
            <select
              id="transfer-department"
              autoFocus
              value={department}
              onChange={(event) => setDepartment(event.target.value)}
              className="mt-2 min-h-11 w-full rounded-xl border border-line bg-white px-3 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal"
            >
              <option>Financial fraud</option>
              <option>Cyber support</option>
              <option>General assistance</option>
            </select>
            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setTransferOpen(false)}
                className="min-h-11 rounded-xl border border-line px-4 text-sm font-semibold hover:bg-canvas"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setTransferOpen(false);
                  setMessage(
                    "Transfer to " +
                      department +
                      " is a demo only. No call was routed.",
                  );
                }}
                className="min-h-11 rounded-xl bg-teal-strong px-4 text-sm font-semibold text-white hover:bg-[#2e6065]"
              >
                Preview transfer
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
