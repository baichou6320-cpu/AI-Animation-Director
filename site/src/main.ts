import {
  ArrowDown,
  Check,
  Clapperboard,
  Copy,
  Github,
  RotateCcw,
  Sparkles,
  Workflow,
  createIcons
} from "lucide";
import "./styles.css";
import { ScrollVideoController } from "./scroll-video";

const base = import.meta.env.BASE_URL;
const mediaRevision = "scrub-v2";
const mediaUrl = (filename: string): string =>
  `${base}media/${filename}?v=${mediaRevision}`;
document.documentElement.style.setProperty(
  "--hero-poster-url",
  `url("${mediaUrl("hero-poster.webp")}")`,
);

createIcons({
  icons: {
    ArrowDown,
    Check,
    Clapperboard,
    Copy,
    Github,
    RotateCcw,
    Sparkles,
    Workflow
  }
});

const video = document.querySelector<HTMLVideoElement>("#hero-video");
const section = document.querySelector<HTMLElement>(".scroll-film");
const progressBar = document.querySelector<HTMLElement>("#film-progress-bar");
const panels = Array.from(
  document.querySelectorAll<HTMLElement>("[data-hero-panel]")
);

const panelStops = [0, 0.14, 0.32, 0.5, 0.68, 0.84];

const setActivePanel = (progress: number): void => {
  let activeIndex = 0;
  for (let index = panelStops.length - 1; index >= 0; index -= 1) {
    if (progress >= panelStops[index]) {
      activeIndex = index;
      break;
    }
  }
  panels.forEach((panel) => {
    panel.classList.toggle(
      "is-active",
      Number(panel.dataset.heroPanel) === activeIndex
    );
  });
  progressBar?.style.setProperty("transform", `scaleX(${progress})`);
  document.documentElement.style.setProperty("--film-progress", String(progress));
};

const assetExists = async (url: string): Promise<boolean> => {
  try {
    const response = await fetch(url, { method: "HEAD", cache: "no-store" });
    return Boolean(
      response.ok &&
        response.headers.get("content-type")?.startsWith("video/"),
    );
  } catch {
    return false;
  }
};

const chooseVideoSource = async (): Promise<string> => {
  const localHostnames = new Set(["localhost", "127.0.0.1"]);
  const mobile = window.matchMedia("(max-width: 700px)").matches;
  const localPrototype = mediaUrl("hero-prototype.mp4");
  if (
    !mobile &&
    localHostnames.has(window.location.hostname) &&
    (await assetExists(localPrototype))
  ) {
    document.body.dataset.mediaMode = "prototype";
    return localPrototype;
  }
  return mediaUrl(mobile ? "hero-mobile.mp4" : "hero-desktop.mp4");
};

if (video && section) {
  video.poster = mediaUrl("hero-poster.webp");
  chooseVideoSource().then((source) => {
    video.src = source;
    video.load();
  });

  const controller = new ScrollVideoController({
    section,
    video,
    onProgress: setActivePanel
  });
  controller.start();
  window.addEventListener("pagehide", () => controller.destroy(), { once: true });
}

setActivePanel(0);

const copyButton = document.querySelector<HTMLButtonElement>("#copy-prompt");
const prompt = "使用 $ai-animation-director，帮我制作一段 AI 动画短片";
copyButton?.addEventListener("click", async () => {
  await navigator.clipboard.writeText(prompt);
  copyButton.replaceChildren();
  const icon = document.createElement("i");
  icon.setAttribute("data-lucide", "check");
  icon.setAttribute("aria-hidden", "true");
  copyButton.append(icon);
  copyButton.setAttribute("aria-label", "已复制");
  copyButton.title = "已复制";
  createIcons({ icons: { Check } });
  window.setTimeout(() => {
    copyButton.replaceChildren();
    const copyIcon = document.createElement("i");
    copyIcon.setAttribute("data-lucide", "copy");
    copyIcon.setAttribute("aria-hidden", "true");
    copyButton.append(copyIcon);
    copyButton.setAttribute("aria-label", "复制开始提示词");
    copyButton.title = "复制";
    createIcons({ icons: { Copy } });
  }, 1600);
});
