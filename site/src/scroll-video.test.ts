import { describe, expect, it } from "vitest";
import {
  clamp,
  progressToVideoTime,
  quantizeVideoTime,
  sectionProgress
} from "./scroll-video";

describe("scroll video math", () => {
  it("clamps values to the requested range", () => {
    expect(clamp(-1)).toBe(0);
    expect(clamp(0.4)).toBe(0.4);
    expect(clamp(2)).toBe(1);
  });

  it("maps the sticky section scroll range to zero through one", () => {
    expect(sectionProgress(100, 100, 3500, 1000)).toBe(0);
    expect(sectionProgress(1350, 100, 3500, 1000)).toBe(0.5);
    expect(sectionProgress(2600, 100, 3500, 1000)).toBe(1);
  });

  it("uses media duration instead of a hard-coded fifteen seconds", () => {
    expect(progressToVideoTime(0, 10.1)).toBe(0);
    expect(progressToVideoTime(0.5, 10.1)).toBeCloseTo(5.03, 2);
    expect(progressToVideoTime(1, 10.1)).toBeCloseTo(10.06, 2);
  });

  it("aligns scroll seeks to real video frames", () => {
    expect(quantizeVideoTime(1.02, 24)).toBeCloseTo(1, 5);
    expect(quantizeVideoTime(1.03, 24)).toBeCloseTo(1.04167, 5);
    expect(quantizeVideoTime(10.2, 24, 10.05)).toBe(10.05);
  });
});
