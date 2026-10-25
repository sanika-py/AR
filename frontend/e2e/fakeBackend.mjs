import { createServer } from "node:http";
import { WebSocketServer } from "ws";

let nextSession = 1;
let dropNextAudio = false;
const sessions = new Map();
const clients = new Set();
const server = createServer((request, response) => {
  if (request.url === "/health") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ status: "ok" }));
    return;
  }
  if (request.url === "/test-state") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(
      JSON.stringify({
        chunks: [...sessions.values()].reduce((sum, value) => sum + value.chunks, 0),
        sizes: [...sessions.values()].flatMap((value) => value.sizes),
        sessions: sessions.size,
      }),
    );
    return;
  }
  if (request.url === "/drop-next-audio") {
    dropNextAudio = true;
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ armed: true }));
    return;
  }
  response.writeHead(404);
  response.end();
});
const sockets = new WebSocketServer({ noServer: true });
server.on("upgrade", (request, socket, head) => {
  sockets.handleUpgrade(request, socket, head, (websocket) => {
    websocket.route = new URL(request.url, "http://localhost").pathname;
    sockets.emit("connection", websocket);
  });
});
sockets.on("connection", (socket) => {
  if (socket.route === "/ws/events") {
    clients.add(socket);
    socket.on("close", () => clients.delete(socket));
    return;
  }
  if (socket.route !== "/ws/audio") {
    socket.close(1008, "Unknown route");
    return;
  }
  const sessionId = "e2e-session-" + nextSession++;
  const session = { chunks: 0, sizes: [] };
  sessions.set(sessionId, session);
  socket.send(JSON.stringify({ type: "session_started", session_id: sessionId }));
  if (dropNextAudio) {
    dropNextAudio = false;
    setTimeout(() => socket.close(1012, "Test reconnect"), 120);
  }
  socket.on("message", (data, isBinary) => {
    if (!isBinary) return;
    session.chunks += 1;
    session.sizes.push(data.byteLength);
    const elapsed = session.chunks / 10;
    const event = {
      type: "analysis",
      session_id: sessionId,
      elapsed,
      scores: [
        { label: "angry", score: 0.05 },
        { label: "calm", score: 0.05 },
        { label: "disgust", score: 0.02 },
        { label: "fearful", score: 0.65 },
        { label: "happy", score: 0.03 },
        { label: "sad", score: 0.12 },
        { label: "surprised", score: 0.08 },
      ],
      indicators: { distress_indicator: 0.52, nervousness_indicator: 0.61 },
      quality_flags: [],
      low_confidence: false,
      category: "Elevated",
    };
    for (const client of clients)
      if (client.readyState === 1) client.send(JSON.stringify(event));
  });
});
server.listen(8000, "127.0.0.1");
