import { chromium } from "playwright";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const root = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const args = Object.fromEntries(process.argv.slice(2).map(s => {
  const [k, v] = s.replace(/^--/, "").split("=");
  return [k, v ?? true];
}));

const fps = Number(args.fps || 30);
const mode = args.mode === "mv" ? "mv" : "douyin";
const isDouyin = mode === "douyin";
const width = Number(args.width || (isDouyin ? 1080 : 1920));
const height = Number(args.height || (isDouyin ? 1920 : 1080));
const duration = Number(args.duration || (args.timeline === "orig91" ? 91.022222 : 86.0));
const out = path.resolve(root, args.out || (isDouyin ? "zaifeixing-v6-douyin-9x16.mp4" : "zaifeixing-v6-widescreen-16x9.mp4"));
const audioPath = path.resolve(root, args.audio || "assets/song.mp3");
const studioHtml = path.resolve(root, "zaifeixing-v6-douyin-studio.html");
const totalFrames = Math.ceil(duration * fps);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height, deviceScaleFactor: 1 } });
await page.goto(url.pathToFileURL(studioHtml).href);
await page.waitForFunction(() => window.ready === true);

// Configure studio canvas to fullscreen for clean frame capture
await page.evaluate(({ mode, timeline, width, height }) => {
  isPlaying = false;
  audioEnabled = false;
  try { bgm.pause(); } catch (e) {}
  if (timeline === "orig91") setTimelineMode("orig91");
  else setTimelineMode("douyin86");
  setCanvasMode(mode);
  document.body.style.margin = "0";
  document.body.style.overflow = "hidden";
  canvas.style.position = "fixed";
  canvas.style.inset = "0";
  canvas.style.width = width + "px";
  canvas.style.height = height + "px";
  canvas.style.zIndex = "99999";
  canvas.style.borderRadius = "0";
  canvas.style.border = "none";
}, { mode, timeline: args.timeline || "douyin86", width, height });

const ffArgs = [
  "-y",
  "-f", "image2pipe",
  "-vcodec", "png",
  "-r", String(fps),
  "-i", "-",
  ...(fs.existsSync(audioPath) ? ["-i", audioPath] : []),
  "-t", duration.toFixed(3),
  "-c:v", "libx264",
  "-preset", args.preset || "medium",
  "-crf", String(args.crf || 18),
  "-pix_fmt", "yuv420p",
  ...(fs.existsSync(audioPath) ? ["-c:a", "aac", "-b:a", "192k", "-shortest"] : []),
  "-movflags", "+faststart",
  out
];

const ff = spawn("ffmpeg", ffArgs, { stdio: ["pipe", "inherit", "inherit"] });

for (let i = 0; i < totalFrames; i++) {
  const t = i / fps;
  await page.evaluate(({ t, isDouyin }) => {
    curTime = t;
    if (isDouyin) renderDouyin916(t);
    else renderAt(t);
  }, { t, isDouyin });
  const buf = await page.locator("canvas").screenshot({ type: "png" });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if (i % (fps * 5) === 0) console.log(`rendered ${(t).toFixed(1)}s / ${duration.toFixed(1)}s (${mode})`);
}

ff.stdin.end();
await new Promise((resolve, reject) => ff.on("close", code => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`))));
await browser.close();
console.log("Exported:", out);
