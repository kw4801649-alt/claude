// render/capture.mjs — deterministic frame capture with headless Chrome (Puppeteer).
//
// Frame i is rendered by calling window.renderAt(i / fps) in the page and taking a
// 1920x1080 screenshot, so every frame is independent of every other frame and of the
// machine's speed. WebGL runs on SwiftShader (software) by default so the pixels are
// the same on any machine with the same Chrome build.
//
// Usage:
//   node render/capture.mjs                      # all frames -> frames/f_00000.png ...
//   node render/capture.mjs --workers 4          # 4 browsers in parallel (same output)
//   node render/capture.mjs --start 0 --end 900  # frames [0, 900) only
//   node render/capture.mjs --resume             # skip frames that already exist
//   node render/capture.mjs --test               # one still per storyboard beat -> renders/test/
//   node render/capture.mjs --gpu                # use the real GPU (faster; pixels may differ by driver)
//   node render/capture.mjs --format jpeg --quality 95   # smaller files
import fs from "node:fs";
import path from "node:path";
import { fork } from "node:child_process";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer";
import { startServer, ROOT } from "./serve.mjs";

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(`--${name}`); return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : def; };
const flag = name => args.includes(`--${name}`);

const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "config", "scenes.json"), "utf8"));
const { width: W, height: H, fps: FPS } = cfg.video;
const TOTAL = cfg.scenes.reduce((s, x) => s + x.duration, 0);
const FRAME_COUNT = Math.round(TOTAL * FPS);
const FORMAT = opt("format", "png");
const EXT = FORMAT === "jpeg" ? "jpg" : "png";
const QUALITY = parseInt(opt("quality", "95"), 10);
const OUT = path.resolve(ROOT, opt("out", flag("test") ? "renders/test" : "frames"));
const GPU = flag("gpu");

const CHROME_ARGS = [
  "--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars", "--mute-audio",
  "--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text",
  "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
  ...(GPU ? ["--enable-gpu", "--ignore-gpu-blocklist"] : ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]),
];

async function openPage(port) {
  const browser = await puppeteer.launch({
    headless: "shell",
    args: CHROME_ARGS,
    defaultViewport: { width: W, height: H, deviceScaleFactor: 1 },
    executablePath: process.env.CHROME_PATH || undefined,
  });
  const page = await browser.newPage();
  page.on("pageerror", e => console.error("[page error]", e.message));
  page.on("console", m => { if (m.type() === "error") console.error("[page console]", m.text()); });
  await page.goto(`http://127.0.0.1:${port}/scene/index.html`, { waitUntil: "load" });
  await page.waitForFunction("window.__ready === true", { timeout: 120000 });
  return { browser, page };
}

async function shoot(page, t, file) {
  await page.evaluate(tt => window.renderAt(tt), t);
  await page.screenshot({ path: file, type: FORMAT, ...(FORMAT === "jpeg" ? { quality: QUALITY } : {}),
    clip: { x: 0, y: 0, width: W, height: H }, captureBeyondViewport: false });
}

// ----------------------------------------------------------------- worker process
if (process.env.CAPTURE_WORKER) {
  const [start, end, port] = process.env.CAPTURE_WORKER.split(",").map(Number);
  const resume = flag("resume");
  const { browser, page } = await openPage(port);
  for (let i = start; i < end; i++) {
    const file = path.join(OUT, `f_${String(i).padStart(5, "0")}.${EXT}`);
    if (!(resume && fs.existsSync(file))) await shoot(page, i / FPS, file);
    process.send({ done: 1 });
  }
  await browser.close();
  process.exit(0);
}

// ----------------------------------------------------------------- main process
fs.mkdirSync(OUT, { recursive: true });
const server = await startServer(0);
const port = server.address().port;

if (flag("test")) {
  // one still per storyboard beat (absolute seconds)
  const starts = {}; let acc = 0;
  for (const s of cfg.scenes) { starts[s.id] = acc; acc += s.duration; }
  const beats = [["s01", 0.6], ["s01", 4], ["s01", 12], ["s02", 5], ["s02", 15], ["s02", 25], ["s02", 37], ["s03", 10], ["s03", 18], ["s03", 23],
    ["s03", 33], ["s03", 46], ["s04", 15], ["s04", 27], ["s05", 6], ["s05", 18], ["s05", 30], ["s05", 38], ["s06", 8], ["s06", 20],
    ["s06", 36], ["s07", 3], ["s07", 10], ["s07", 13], ["s07", 20], ["s07", 30], ["s07", 38], ["s08", 6], ["s08", 13], ["s08", 32],
    ["s09", 10], ["s09", 22], ["s09", 33], ["s10", 6], ["s10", 15]];
  const times = (opt("times", "") || "").split(",").filter(Boolean).map(Number);
  const list = times.length ? times.map(t => [`t${t}`, t]) : beats.map(([id, l]) => [`${id}_${String(l).replace(".", "p")}`, starts[id] + l]);
  const { browser, page } = await openPage(port);
  for (const [name, t] of list) {
    const file = path.join(OUT, `${name}.${EXT}`);
    const t0 = Date.now();
    await shoot(page, Math.round(t * FPS) / FPS, file);
    console.log(`${file}  (t=${t.toFixed(2)}s, ${Date.now() - t0} ms)`);
  }
  await browser.close(); server.close();
  process.exit(0);
}

const start = parseInt(opt("start", "0"), 10);
const end = Math.min(parseInt(opt("end", String(FRAME_COUNT)), 10), FRAME_COUNT);
const workers = Math.max(1, parseInt(opt("workers", "1"), 10));
const total = end - start;
console.log(`Rendering frames ${start}..${end - 1} of ${FRAME_COUNT} (${TOTAL}s @ ${FPS} fps, ${W}x${H}) -> ${OUT}`);
console.log(`Workers: ${workers}, format: ${FORMAT}, WebGL: ${GPU ? "GPU" : "SwiftShader (deterministic)"}`);

let done = 0;
const t0 = Date.now();
const chunk = Math.ceil(total / workers);
const jobs = [];
for (let w = 0; w < workers; w++) {
  const a = start + w * chunk, b = Math.min(end, a + chunk);
  if (a >= b) continue;
  jobs.push(new Promise((resolve, reject) => {
    const child = fork(fileURLToPath(import.meta.url), args, { env: { ...process.env, CAPTURE_WORKER: `${a},${b},${port}` } });
    child.on("message", () => {
      done++;
      if (done % 30 === 0 || done === total) {
        const el = (Date.now() - t0) / 1000, rate = done / el, eta = (total - done) / rate;
        process.stdout.write(`\r  ${done}/${total} frames  ${rate.toFixed(2)} fps  ETA ${Math.floor(eta / 60)}m${String(Math.round(eta % 60)).padStart(2, "0")}s   `);
      }
    });
    child.on("exit", code => (code === 0 ? resolve() : reject(new Error(`worker ${w} exited with ${code}`))));
  }));
}
try {
  await Promise.all(jobs);
  console.log(`\nDone in ${((Date.now() - t0) / 60000).toFixed(1)} min.`);
} finally { server.close(); }
