export const clamp = (value: number, minimum = 0, maximum = 1): number =>
  Math.min(maximum, Math.max(minimum, value));

export const sectionProgress = (
  scrollY: number,
  sectionTop: number,
  sectionHeight: number,
  viewportHeight: number
): number => {
  const scrollRange = Math.max(sectionHeight - viewportHeight, 1);
  return clamp((scrollY - sectionTop) / scrollRange);
};

export const progressToVideoTime = (
  progress: number,
  duration: number,
  endPadding = 0.04
): number => {
  const playableDuration = Math.max(duration - endPadding, 0);
  return clamp(progress) * playableDuration;
};

export const quantizeVideoTime = (
  time: number,
  mediaFps = 24,
  maximum = Number.POSITIVE_INFINITY
): number => {
  const safeFps = Math.max(mediaFps, 1);
  const frameAligned = Math.round(Math.max(time, 0) * safeFps) / safeFps;
  return Math.min(frameAligned, maximum);
};

type ScrollVideoOptions = {
  section: HTMLElement;
  video: HTMLVideoElement;
  onProgress?: (progress: number) => void;
  mediaFps?: number;
  maxSeekFps?: number;
  reducedMotion?: MediaQueryList;
};

export class ScrollVideoController {
  private readonly section: HTMLElement;
  private readonly video: HTMLVideoElement;
  private readonly onProgress?: (progress: number) => void;
  private readonly mediaFps: number;
  private readonly frameDuration: number;
  private readonly minimumSeekInterval: number;
  private readonly reducedMotion: MediaQueryList;
  private targetTime = 0;
  private lastAppliedTime = -1;
  private lastSeekAt = Number.NEGATIVE_INFINITY;
  private frameId = 0;
  private sectionTop = 0;
  private visible = true;
  private disposed = false;

  constructor({
    section,
    video,
    onProgress,
    mediaFps = 24,
    maxSeekFps = 12,
    reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)")
  }: ScrollVideoOptions) {
    this.section = section;
    this.video = video;
    this.onProgress = onProgress;
    this.mediaFps = Math.max(mediaFps, 1);
    this.frameDuration = 1 / this.mediaFps;
    this.minimumSeekInterval = 1000 / Math.max(maxSeekFps, 1);
    this.reducedMotion = reducedMotion;

    this.handleScroll = this.handleScroll.bind(this);
    this.handleResize = this.handleResize.bind(this);
    this.handleVisibility = this.handleVisibility.bind(this);
    this.tick = this.tick.bind(this);
  }

  start(): void {
    this.video.pause();
    this.video.addEventListener("loadedmetadata", this.handleResize);
    window.addEventListener("scroll", this.handleScroll, { passive: true });
    window.addEventListener("resize", this.handleResize, { passive: true });
    document.addEventListener("visibilitychange", this.handleVisibility);
    this.reducedMotion.addEventListener("change", this.handleResize);
    this.handleResize();
    this.frameId = requestAnimationFrame(this.tick);
  }

  destroy(): void {
    this.disposed = true;
    cancelAnimationFrame(this.frameId);
    this.video.removeEventListener("loadedmetadata", this.handleResize);
    window.removeEventListener("scroll", this.handleScroll);
    window.removeEventListener("resize", this.handleResize);
    document.removeEventListener("visibilitychange", this.handleVisibility);
    this.reducedMotion.removeEventListener("change", this.handleResize);
  }

  private measure(): void {
    this.sectionTop = window.scrollY + this.section.getBoundingClientRect().top;
  }

  private handleResize(): void {
    this.measure();
    this.handleScroll();
  }

  private handleScroll(): void {
    const progress = sectionProgress(
      window.scrollY,
      this.sectionTop,
      this.section.offsetHeight,
      window.innerHeight
    );
    this.onProgress?.(progress);
    if (!this.reducedMotion.matches && Number.isFinite(this.video.duration)) {
      this.targetTime = progressToVideoTime(progress, this.video.duration);
    }
  }

  private handleVisibility(): void {
    this.visible = document.visibilityState === "visible";
    if (this.visible) {
      this.handleScroll();
    }
  }

  private tick(timestamp: number): void {
    if (this.disposed) {
      return;
    }

    if (
      this.visible &&
      !this.reducedMotion.matches &&
      this.video.readyState >= HTMLMediaElement.HAVE_METADATA &&
      Number.isFinite(this.video.duration) &&
      !this.video.seeking &&
      timestamp - this.lastSeekAt >= this.minimumSeekInterval
    ) {
      const nextTime = quantizeVideoTime(
        this.targetTime,
        this.mediaFps,
        Math.max(this.video.duration - this.frameDuration, 0)
      );
      if (Math.abs(nextTime - this.lastAppliedTime) >= this.frameDuration / 2) {
        this.video.currentTime = nextTime;
        this.lastAppliedTime = nextTime;
        this.lastSeekAt = timestamp;
      }
    }
    this.frameId = requestAnimationFrame(this.tick);
  }
}
