import { useEffect, useRef } from "react";
import uPlot from "uplot";
import type { MockCall } from "./mockData";

export function MockWaveform({ seed }: { seed: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (!canvas || !context) return;
    const width = canvas.clientWidth || 520;
    const height = 96;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.scale(ratio, ratio);
    context.clearRect(0, 0, width, height);
    context.strokeStyle = "#4f8f94";
    context.lineWidth = 2;
    context.beginPath();
    for (let x = 0; x < width; x += 2) {
      const envelope = 0.2 + 0.8 * Math.abs(Math.sin(x / 94 + seed));
      const wave = Math.sin(x * 0.105 + seed) * 13 + Math.sin(x * 0.031 + seed * 2) * 7;
      const y = height / 2 + wave * envelope;
      if (x === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    }
    context.stroke();
  }, [seed]);
  return (
    <canvas
      ref={canvasRef}
      className="h-24 w-full"
      role="img"
      aria-label="Advisory mock waveform visualization; no live audio is connected."
    />
  );
}

export function LiveWaveform({ samples }: { samples: number[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (!canvas || !context) return;
    const width = canvas.clientWidth || 520;
    const height = 96;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.scale(ratio, ratio);
    context.clearRect(0, 0, width, height);
    context.strokeStyle = "#376f74";
    context.lineWidth = 2;
    context.beginPath();
    samples.forEach((sample, index) => {
      const x = (index / Math.max(samples.length - 1, 1)) * width;
      const y = height / 2 - sample * (height * 0.44);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.stroke();
  }, [samples]);
  return (
    <canvas
      ref={canvasRef}
      className="h-24 w-full"
      role="img"
      aria-label="Live waveform display. Audio is processed in memory and not saved."
    />
  );
}

export function TrajectoryChart({ call }: { call: MockCall }) {
  const hostRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const chart = new uPlot(
      {
        width: Math.max(host.clientWidth, 280),
        height: 176,
        scales: { y: { range: [0, 1] } },
        axes: [
          { stroke: "#526a6d", grid: { stroke: "#d9e5e5", width: 1 } },
          {
            stroke: "#526a6d",
            grid: { stroke: "#d9e5e5", width: 1 },
            values: (_plot, ticks) => ticks.map((value) => Number(value).toFixed(1)),
          },
        ],
        series: [
          {},
          {
            label: "Distress · Advisory",
            stroke: "#a75d55",
            width: 2,
            points: { show: false },
          },
          {
            label: "Nervousness · Advisory",
            stroke: "#8a5b14",
            width: 2,
            points: { show: false },
          },
        ],
        legend: { show: true, live: false },
        cursor: { show: false },
      },
      [call.distress.map((_value, index) => index), call.distress, call.nervousness],
      host,
    );
    return () => chart.destroy();
  }, [call.id, call.distress, call.nervousness]);
  return (
    <div
      ref={hostRef}
      className="trajectory-chart min-w-0 overflow-hidden"
      role="img"
      aria-label="Advisory emotional trajectory chart showing mock distress and nervousness signals across recent windows."
    />
  );
}
