import { expect, test } from "@playwright/test";

test("selecting a queue card updates the detail panel and keeps actions labelled as demo", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Caller 4821" })).toBeVisible();
  await page.getByRole("button", { name: /Caller 1907/ }).click();
  await expect(page.getByRole("heading", { name: "Caller 1907" })).toBeVisible();
  await expect(page.getByText(/AR-2046 · Mumbai/)).toBeVisible();
  await expect(page.getByText(/Advisory signal:/).first()).toBeVisible();

  await page.getByRole("button", { name: "Escalate" }).click();
  await expect(page.getByText(/Escalate is a demo only/)).toBeVisible();
  await page.getByRole("button", { name: "Flag for Review" }).click();
  await expect(page.getByText("Flagged for review")).toBeVisible();

  await page.getByRole("button", { name: "Transfer" }).click();
  const dialog = page.getByRole("dialog", { name: /Transfer · Demo/ });
  await expect(dialog).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
});
