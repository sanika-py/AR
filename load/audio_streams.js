import ws from "k6/ws";
import { check, sleep } from "k6";
import { Counter, Trend } from "k6/metrics";

const connected = new Counter("audio_stream_connections");
const connectionErrors = new Counter("audio_stream_connection_errors");
const sessionStarted = new Counter("audio_stream_sessions_started");
const sentChunks = new Counter("audio_stream_chunks_sent");
const connectionLatency = new Trend("audio_stream_connection_latency_ms");

const baseUrl = __ENV.WS_BASE_URL || "ws://127.0.0.1:8000";
const streamDuration = __ENV.STREAM_SECONDS || "30";

export const options = {
  scenarios: {
    concurrent_audio_streams: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "10s", target: 20 },
        { duration: `${streamDuration}s`, target: 20 },
        { duration: "5s", target: 0 },
      ],
      gracefulRampDown: "5s",
    },
  },
  thresholds: {
    audio_stream_connection_errors: ["count==0"],
    audio_stream_connection_latency_ms: ["p(95)<2000"],
  },
};

export default function () {
  const started = Date.now();
  const response = ws.connect(`${baseUrl}/ws/audio`, {}, (socket) => {
    socket.on("open", () => {
      connected.add(1);
      connectionLatency.add(Date.now() - started);
      const pcmSilence = new Uint8Array(3200); // 100 ms mono PCM16 at 16 kHz; synthetic only.
      socket.setInterval(() => {
        if (socket.readyState === 1) {
          socket.sendBinary(pcmSilence.buffer);
          sentChunks.add(1);
        }
      }, 100);
    });
    socket.on("message", (message) => {
      try {
        if (JSON.parse(message).type === "session_started") sessionStarted.add(1);
      } catch (_) {
        // Non-JSON server messages do not count as a valid session handshake.
      }
    });
    socket.on("error", () => connectionErrors.add(1));
    socket.setTimeout(() => socket.close(), Number(streamDuration) * 1000);
  });

  check(response, { "audio websocket accepted": (res) => res && res.status === 101 });
  if (!response || response.status !== 101) connectionErrors.add(1);
  sleep(0.1);
}
