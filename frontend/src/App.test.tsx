import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./Charts", () => ({
  MockWaveform: () => <div role="img" aria-label="Advisory mock waveform" />,
  TrajectoryChart: () => (
    <div role="img" aria-label="Advisory emotional trajectory chart" />
  ),
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("mock call dashboard", () => {
  it("updates the detail panel when an officer selects a queue card", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Caller 4821" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Caller 1907/ }));
    expect(screen.getByRole("heading", { name: "Caller 1907" })).toBeTruthy();
    expect(screen.getByText(/AR-2046 · Mumbai/)).toBeTruthy();
    expect(screen.getByText(/I gave them a code from my phone/)).toBeTruthy();
  });

  it("keeps review flag controls local and labelled", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Flag for Review" }));
    expect(
      screen
        .getByRole("button", { name: "Unflag review" })
        .getAttribute("aria-pressed"),
    ).toBe("true");
    expect(screen.getByText("Flagged for review")).toBeTruthy();
  });

  it("offers a demo only escalation message", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Escalate" }));
    expect(screen.getAllByRole("status")[1].textContent).toContain(
      "No operational action was sent",
    );
  });
});
