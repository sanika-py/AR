import { useEffect, useRef, useState } from "react";
import { useAnalysisStore } from "./store";
import { createPcmCapture } from "./liveAudio";
import { isServerEvent } from "./types";
import type { CaptureHandle } from "./liveAudio";

export type LiveStatus =
  "idle" | "requesting" | "connecting" | "listening" | "reconnecting" | "error";
type SocketKind = "audio" | "events";

function socketUrl(path: string): string {
  const base = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const url = new URL(path, base);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

function permissionMessage(error: unknown): string {
  if (error instanceof DOMException && error.name === "NotAllowedError") {
    return "Microphone permission denied. Allow microphone access in your browser settings, then try again.";
  }
  if (error instanceof DOMException && error.name === "NotFoundError") {
    return "No microphone was found. Connect a microphone and try again.";
  }
  return error instanceof Error ? error.message : "Unable to start microphone capture.";
}

export function useLiveAudio(enabled: boolean) {
  const [status, setStatus] = useState<LiveStatus>("idle");
  const [error, setError] = useState("");
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [sessionActive, setSessionActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [asrEnabled, setAsrEnabled] = useState(false);
  const [waveform, setWaveform] = useState<number[]>([]);
  const captureRef = useRef<CaptureHandle | null>(null);
  const audioSocketRef = useRef<WebSocket | null>(null);
  const eventSocketRef = useRef<WebSocket | null>(null);
  const desiredRef = useRef(false);
  const sessionIdRef = useRef<string | null>(null);
  const audioOpenedAtRef = useRef(0);
  const attemptsRef = useRef<Record<SocketKind, number>>({ audio: 0, events: 0 });
  const timersRef = useRef<Partial<Record<SocketKind, number>>>({});

  useEffect(
    () => () => {
      desiredRef.current = false;
      Object.values(timersRef.current).forEach((timer) => {
        if (timer !== undefined) window.clearTimeout(timer);
      });
      void captureRef.current?.close();
      audioSocketRef.current?.close();
      eventSocketRef.current?.close();
    },
    [],
  );

  function setConnectionStatus() {
    if (!desiredRef.current) return;
    if (
      audioSocketRef.current?.readyState === WebSocket.OPEN &&
      eventSocketRef.current?.readyState === WebSocket.OPEN &&
      sessionIdRef.current
    ) {
      setStatus("listening");
      setError("");
    } else {
      setStatus("connecting");
    }
  }

  function scheduleReconnect(kind: SocketKind, reconnect: () => void) {
    if (!desiredRef.current || timersRef.current[kind] !== undefined) return;
    setStatus("reconnecting");
    const attempt = attemptsRef.current[kind];
    attemptsRef.current[kind] = attempt + 1;
    const delay = Math.min(8000, 500 * 2 ** Math.min(attempt, 4));
    timersRef.current[kind] = window.setTimeout(() => {
      delete timersRef.current[kind];
      reconnect();
    }, delay);
  }

  function connectEvents() {
    if (!desiredRef.current) return;
    let socket: WebSocket;
    try {
      socket = new WebSocket(socketUrl("/ws/events"));
    } catch (socketError) {
      setError(permissionMessage(socketError));
      scheduleReconnect("events", connectEvents);
      return;
    }
    eventSocketRef.current = socket;
    socket.onopen = () => {
      if (eventSocketRef.current !== socket) return;
      attemptsRef.current.events = 0;
      setConnectionStatus();
    };
    socket.onmessage = (message) => {
      if (eventSocketRef.current !== socket || typeof message.data !== "string") return;
      try {
        const value: unknown = JSON.parse(message.data);
        if (!isServerEvent(value) || value.session_id !== sessionIdRef.current) return;
        useAnalysisStore.getState().receiveEvent(value);
        if (value.type === "analysis") {
          const elapsed = (performance.now() - audioOpenedAtRef.current) / 1000;
          setLatencyMs(Math.round(Math.max(0, elapsed - value.elapsed) * 1000));
          setStatus("listening");
          setError("");
        } else if (value.type === "analysis_error") {
          setStatus("error");
          setError(value.message);
        }
      } catch {
        // Ignore malformed or unrelated event payloads.
      }
    };
    socket.onerror = () => socket.close();
    socket.onclose = () => {
      if (eventSocketRef.current !== socket) return;
      scheduleReconnect("events", connectEvents);
    };
  }

  function connectAudio() {
    if (!desiredRef.current) return;
    let socket: WebSocket;
    try {
      socket = new WebSocket(socketUrl("/ws/audio"));
      socket.binaryType = "arraybuffer";
    } catch (socketError) {
      setError(permissionMessage(socketError));
      scheduleReconnect("audio", connectAudio);
      return;
    }
    audioSocketRef.current = socket;
    socket.onopen = () => {
      if (audioSocketRef.current !== socket) return;
      audioOpenedAtRef.current = performance.now();
      attemptsRef.current.audio = 0;
      setConnectionStatus();
    };
    socket.onmessage = (message) => {
      if (audioSocketRef.current !== socket || typeof message.data !== "string") return;
      try {
        const value = JSON.parse(message.data) as {
          type?: unknown;
          session_id?: unknown;
          asr_enabled?: unknown;
        };
        if (value.type === "session_started" && typeof value.session_id === "string") {
          sessionIdRef.current = value.session_id;
          setSessionId(value.session_id);
          setAsrEnabled(value.asr_enabled === true);
          setLatencyMs(null);
          setSessionActive(true);
          useAnalysisStore.getState().reset();
          setConnectionStatus();
        }
      } catch {
        // The audio socket's binary input stream does not require other responses.
      }
    };
    socket.onerror = () => socket.close();
    socket.onclose = () => {
      if (audioSocketRef.current !== socket) return;
      sessionIdRef.current = null;
      setSessionId(null);
      setAsrEnabled(false);
      setSessionActive(false);
      useAnalysisStore.getState().reset();
      scheduleReconnect("audio", connectAudio);
    };
  }

  async function start() {
    if (!enabled || desiredRef.current) return;
    desiredRef.current = true;
    setRecording(true);
    setStatus("requesting");
    setError("");
    setLatencyMs(null);
    try {
      const capture = await createPcmCapture((chunk) => {
        const rawSamples = new Int16Array(chunk);
        const pointCount = 64;
        const points = Array.from({ length: pointCount }, (_, index) => {
          const sampleIndex = Math.min(
            rawSamples.length - 1,
            Math.floor((index / pointCount) * rawSamples.length),
          );
          return rawSamples[sampleIndex] / 32768;
        });
        setWaveform(points);
        const socket = audioSocketRef.current;
        if (
          desiredRef.current &&
          sessionIdRef.current &&
          socket?.readyState === WebSocket.OPEN
        ) {
          socket.send(chunk);
        }
      });
      if (!desiredRef.current) {
        await capture.close();
        return;
      }
      captureRef.current = capture;
      connectEvents();
      connectAudio();
      setStatus("connecting");
    } catch (captureError) {
      desiredRef.current = false;
      setRecording(false);
      setStatus("error");
      setError(permissionMessage(captureError));
      await captureRef.current?.close();
      captureRef.current = null;
    }
  }

  async function stop() {
    desiredRef.current = false;
    setRecording(false);
    Object.values(timersRef.current).forEach((timer) => {
      if (timer !== undefined) window.clearTimeout(timer);
    });
    timersRef.current = {};
    sessionIdRef.current = null;
    setSessionId(null);
    setAsrEnabled(false);
    setSessionActive(false);
    setLatencyMs(null);
    setWaveform([]);
    setStatus("idle");
    setError("");
    await captureRef.current?.close();
    captureRef.current = null;
    audioSocketRef.current?.close();
    eventSocketRef.current?.close();
    audioSocketRef.current = null;
    eventSocketRef.current = null;
    useAnalysisStore.getState().reset();
  }

  return {
    status,
    error,
    latencyMs,
    recording,
    sessionActive,
    sessionId,
    asrEnabled,
    waveform,
    start,
    stop,
  };
}
