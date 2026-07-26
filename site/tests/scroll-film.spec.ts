import { expect, test } from "@playwright/test";

test("scrolling forward and backward scrubs the hero video", async ({ page }) => {
  await page.goto("/");
  const video = page.locator("#hero-video");
  await expect(video).toBeVisible();
  await page.waitForFunction(() => {
    const element = document.querySelector<HTMLVideoElement>("#hero-video");
    return Boolean(element && Number.isFinite(element.duration));
  });

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.45));
  await page.waitForTimeout(900);
  const forwardTime = await video.evaluate((element) => element.currentTime);
  expect(forwardTime).toBeGreaterThan(1);

  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(900);
  const reverseTime = await video.evaluate((element) => element.currentTime);
  expect(reverseTime).toBeLessThan(forwardTime);
  expect(reverseTime).toBeLessThan(0.5);
});

test("the first viewport keeps the product name readable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /AI Animation Director/i })).toBeVisible();
  await expect(page.locator("header")).toBeVisible();
  await expect(page.locator(".film-progress")).toBeVisible();
});

test("the hero uses a bounded crop instead of full-screen cover", async ({ page }) => {
  await page.goto("/");
  const layout = await page.locator("#hero-video").evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return {
      objectFit: getComputedStyle(element).objectFit,
      videoWidth: rect.width,
      viewportWidth: document.documentElement.clientWidth
    };
  });

  expect(layout.objectFit).toBe("contain");
  expect(layout.videoWidth).toBeGreaterThanOrEqual(layout.viewportWidth);
  expect(layout.videoWidth).toBeLessThanOrEqual(layout.viewportWidth * 1.121);
});

test("reduced motion keeps a poster and disables visible video", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expect(page.locator(".hero-poster")).toBeVisible();
  await expect(page.locator("#hero-video")).toHaveCSS("display", "none");
});
