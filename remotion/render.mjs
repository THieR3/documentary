// Bundles once, then renders video chunks (muted) or QA stills.
// Usage:
//   node render.mjs chunks <props.json> <mediaDir> <outDir> [--chunk-sec 60] [--scale 1] [--concurrency N] [--max-frames N]
//   node render.mjs stills <props.json> <mediaDir> <outDir> [--scale 0.5] [--frames 10,200,...]
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const [mode, propsPath, mediaDir, outDir, ...rest] = process.argv.slice(2);
if (!mode || !propsPath || !mediaDir || !outDir) {
  console.error("usage: node render.mjs <chunks|stills> <props.json> <mediaDir> <outDir> [options]");
  process.exit(2);
}
const opt = (name, def) => {
  const i = rest.indexOf(`--${name}`);
  return i >= 0 ? rest[i + 1] : def;
};

// Use a local Chrome when the Remotion download host is unreachable (e.g. preinstalled Playwright headless shell).
const localBrowser =
  process.env.REMOTION_BROWSER ||
  ["/opt/pw-browsers/chromium_headless_shell", "/opt/pw-browsers/chromium"].find((p) => fs.existsSync(p)) ||
  null;
// Wrapper re-enables HTTPS_PROXY inside Chrome (Remotion passes --no-proxy-server), needed for Google Fonts.
let browserExecutable = null;
if (localBrowser) {
  process.env.REMOTION_REAL_BROWSER = localBrowser;
  browserExecutable = path.join(here, "chrome-wrapper.sh");
  console.log(`[browser] ${localBrowser} (via chrome-wrapper.sh)`);
}
const chromiumOptions = { gl: "swangle" };

const inputProps = JSON.parse(fs.readFileSync(propsPath, "utf8"));
fs.mkdirSync(outDir, { recursive: true });

console.log(`[bundle] public dir = ${mediaDir}`);
const serveUrl = await bundle({ entryPoint: path.join(here, "src", "index.ts"), publicDir: path.resolve(mediaDir) });
const composition = await selectComposition({ serveUrl, id: "Documentary", inputProps, browserExecutable, chromiumOptions });
const scale = Number(opt("scale", mode === "stills" ? "0.5" : "1"));
const concurrency = Number(opt("concurrency", String(Math.max(1, Math.floor(os.cpus().length * 0.75)))));

if (mode === "stills") {
  const frames = opt("frames", "")
    .split(",")
    .filter(Boolean)
    .map(Number);
  const list = frames.length
    ? frames
    : inputProps.segments.map((s) => Math.min(inputProps.totalFrames - 1, s.startFrame + Math.floor(s.durationFrames * 0.6)));
  for (const f of list) {
    const output = path.join(outDir, `f${String(f).padStart(6, "0")}.jpg`);
    await renderStill({ composition, serveUrl, inputProps, frame: f, output, scale, imageFormat: "jpeg", jpegQuality: 80, browserExecutable, chromiumOptions });
    console.log(`[still] ${output}`);
  }
  process.exit(0);
}

if (mode === "chunks") {
  const fps = composition.fps;
  const total = Math.min(composition.durationInFrames, Number(opt("max-frames", String(composition.durationInFrames))));
  const chunk = Math.round(Number(opt("chunk-sec", "60")) * fps);
  const list = [];
  for (let a = 0, i = 0; a < total; a += chunk, i++) list.push({ i, a, b: Math.min(total, a + chunk) - 1 });
  const t0 = Date.now();
  for (const { i, a, b } of list) {
    const out = path.join(outDir, `c${String(i).padStart(4, "0")}.mp4`);
    if (fs.existsSync(out) && fs.existsSync(out + ".done")) {
      console.log(`[skip] ${out}`);
      continue;
    }
    let last = -1;
    await renderMedia({
      composition,
      serveUrl,
      inputProps,
      codec: "h264",
      crf: Number(opt("crf", "19")),
      pixelFormat: "yuv420p",
      muted: true,
      imageFormat: "jpeg",
      jpegQuality: 90,
      frameRange: [a, b],
      outputLocation: out,
      scale,
      concurrency,
      browserExecutable,
      chromiumOptions,
      onProgress: ({ progress }) => {
        const pct = Math.floor(progress * 100);
        if (pct % 10 === 0 && pct !== last) {
          last = pct;
          console.log(`[chunk ${i + 1}/${list.length}] ${pct}%  (frames ${a}-${b}, ${((Date.now() - t0) / 60000).toFixed(1)} min elapsed)`);
        }
      },
    });
    fs.writeFileSync(out + ".done", "");
  }
  fs.writeFileSync(path.join(outDir, "list.txt"), list.map(({ i }) => `file 'c${String(i).padStart(4, "0")}.mp4'`).join("\n") + "\n");
  console.log(`[done] ${list.length} chunks in ${((Date.now() - t0) / 60000).toFixed(1)} min`);
  process.exit(0);
}

console.error(`unknown mode ${mode}`);
process.exit(2);
