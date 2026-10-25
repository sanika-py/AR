export type Priority = "P1" | "P2" | "P3" | "P4";

export interface MockCall {
  id: string;
  urgency?: number;
  priority?: Priority;
  category?: "Routine" | "Elevated" | "High";
  durationSeconds: number;
  caller: string;
  location: string;
  agent: string;
  insight: string;
  keywords: string[];
  transcript: string[];
  distress: number[];
  nervousness: number[];
  waveformSeed: number;
  notes: string;
}

const demoCalls: Array<MockCall & { urgency: number; priority: Priority }> = [
  {
    id: "AR-2048",
    urgency: 9.2,
    priority: "P1",
    durationSeconds: 318,
    caller: "Caller 4821",
    location: "Pune · Kothrud",
    agent: "A. Deshmukh",
    insight:
      "Advisory signal: fear and distress scores have increased in recent windows.",
    keywords: ["threatened", "urgent transfer"],
    transcript: [
      "Caller: They said I had to move the money now.",
      "Caller: I don't know what to do next.",
    ],
    distress: [0.24, 0.29, 0.27, 0.34, 0.42, 0.48, 0.55, 0.59],
    nervousness: [0.2, 0.23, 0.31, 0.28, 0.39, 0.44, 0.49, 0.52],
    waveformSeed: 4,
    notes: "Demo note: confirm the caller is in a safe place.",
  },
  {
    id: "AR-2046",
    urgency: 7.6,
    priority: "P2",
    durationSeconds: 194,
    caller: "Caller 1907",
    location: "Mumbai · Andheri",
    agent: "R. Patil",
    insight: "Advisory signal: vocal energy varies across the recent sample.",
    keywords: ["OTP shared", "bank"],
    transcript: [
      "Caller: I gave them a code from my phone.",
      "Caller: They told me it was for verification.",
    ],
    distress: [0.3, 0.31, 0.36, 0.34, 0.4, 0.38, 0.44, 0.42],
    nervousness: [0.37, 0.4, 0.39, 0.44, 0.46, 0.43, 0.5, 0.48],
    waveformSeed: 9,
    notes: "",
  },
  {
    id: "AR-2045",
    urgency: 5.1,
    priority: "P3",
    durationSeconds: 126,
    caller: "Caller 7210",
    location: "Nashik · College Road",
    agent: "S. Kulkarni",
    insight:
      "Advisory signal: emotion scores are mixed; review the conversation context.",
    keywords: ["account access"],
    transcript: [
      "Caller: I cannot log into my account.",
      "Caller: I received a message about a hold.",
    ],
    distress: [0.2, 0.25, 0.23, 0.29, 0.26, 0.31, 0.28, 0.3],
    nervousness: [0.22, 0.21, 0.27, 0.3, 0.29, 0.31, 0.28, 0.32],
    waveformSeed: 13,
    notes: "",
  },
  {
    id: "AR-2042",
    urgency: 3.4,
    priority: "P4",
    durationSeconds: 63,
    caller: "Caller 5334",
    location: "Satara · Central",
    agent: "M. Jadhav",
    insight:
      "Advisory signal: no single emotion score is prominent in this mock window.",
    keywords: ["online payment"],
    transcript: [
      "Caller: I noticed a small payment I don't recognise.",
      "Caller: I would like some guidance.",
    ],
    distress: [0.14, 0.16, 0.17, 0.15, 0.18, 0.17, 0.2, 0.18],
    nervousness: [0.16, 0.15, 0.19, 0.18, 0.2, 0.19, 0.22, 0.21],
    waveformSeed: 7,
    notes: "",
  },
];

/** Deterministic mock event source. Real backend events will replace this data. */
export function generateMockCalls(tick = 0): MockCall[] {
  return demoCalls
    .map((call, index) => ({
      ...call,
      durationSeconds: call.durationSeconds + tick,
      urgency: Math.max(
        1,
        Math.min(
          10,
          Number((call.urgency + Math.sin((tick + index * 7) / 20) * 0.12).toFixed(1)),
        ),
      ),
    }))
    .sort((a, b) => b.urgency - a.urgency);
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const remainder = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return minutes + ":" + remainder;
}
