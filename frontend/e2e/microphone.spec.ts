import { expect, test } from "@playwright/test";

test("authorised fake microphone sends 100 ms PCM16 chunks and renders backend events", async ({
  page,
  request,
}) => {
  await page.goto("/");
  const consent = page.getByRole("checkbox", {
    name: "I am authorised to record this call.",
  });
  const start = page.getByRole("button", { name: "Start call recording" });
  await expect(start).toBeDisabled();
  await consent.check();
  await expect(start).toBeEnabled();
  await request.get("http://127.0.0.1:8000/drop-next-audio");
  await start.click();

  await expect(
    page.getByRole("heading", { name: "Live microphone session" }),
  ).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText(/Top raw model label: fearful/)).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByText(/Observed analysis latency: \d+ ms/)).toBeVisible({
    timeout: 10_000,
  });

  await expect
    .poll(
      async () => {
        const response = await request.get("http://127.0.0.1:8000/test-state");
        const state = (await response.json()) as {
          chunks: number;
          sizes: number[];
          sessions: number;
        };
        return (
          state.chunks > 0 &&
          state.sessions >= 2 &&
          state.sizes.every((size) => size === 3200)
        );
      },
      { timeout: 10_000 },
    )
    .toBe(true);

  await page.getByRole("button", { name: "Stop recording" }).click();
  await expect(page.getByText("Not recording").first()).toBeVisible();
});

test("microphone permission denial is explained before any socket is opened", async ({
  page,
}) => {
  const apiSockets: string[] = [];
  page.on("websocket", (socket) => {
    const url = socket.url();
    if (url.includes("/ws/")) apiSockets.push(url);
  });
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: {
        getUserMedia: () =>
          Promise.reject(new DOMException("Permission denied", "NotAllowedError")),
      },
    });
  });
  await page.goto("/");
  await page
    .getByRole("checkbox", { name: "I am authorised to record this call." })
    .check();
  await page.getByRole("button", { name: "Start call recording" }).click();
  await expect(page.getByText(/Microphone permission denied/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Start call recording" }),
  ).toBeEnabled();
  expect(apiSockets).toEqual([]);
});
