// render/serve.mjs — tiny dependency-free static file server for the project root.
// ES modules cannot be loaded from file://, so both the preview and the frame capture
// load the scene over http://127.0.0.1.
//
//   node render/serve.mjs            -> serves on http://127.0.0.1:8080
//   PORT=9000 node render/serve.mjs  -> custom port
//   then open http://127.0.0.1:8080/scene/index.html?preview=1
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".css": "text/css; charset=utf-8", ".woff2": "font/woff2", ".woff": "font/woff",
  ".wav": "audio/wav", ".mp3": "audio/mpeg", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".srt": "text/plain; charset=utf-8",
};

export function startServer(port = 0, host = "127.0.0.1") {
  const server = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const file = path.normalize(path.join(ROOT, urlPath));
    if (!file.startsWith(ROOT)) { res.writeHead(403); res.end("forbidden"); return; }
    fs.stat(file, (err, stat) => {
      if (err || !stat.isFile()) { res.writeHead(404); res.end("not found"); return; }
      const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
      const range = req.headers.range;
      if (range && /^bytes=\d*-\d*$/.test(range)) {           // lets <audio> seek in preview mode
        let [a, b] = range.slice(6).split("-");
        const start = a ? parseInt(a, 10) : 0, end = b ? parseInt(b, 10) : stat.size - 1;
        res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${start}-${end}/${stat.size}`, "Accept-Ranges": "bytes", "Content-Length": end - start + 1 });
        fs.createReadStream(file, { start, end }).pipe(res);
        return;
      }
      res.writeHead(200, { "Content-Type": type, "Content-Length": stat.size, "Accept-Ranges": "bytes", "Cache-Control": "no-cache" });
      fs.createReadStream(file).pipe(res);
    });
  });
  return new Promise(resolve => server.listen(port, host, () => resolve(server)));
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = parseInt(process.env.PORT || "8080", 10);
  const server = await startServer(port);
  const { port: p } = server.address();
  console.log(`Serving ${ROOT}`);
  console.log(`Preview:  http://127.0.0.1:${p}/scene/index.html?preview=1`);
  console.log(`Still:    http://127.0.0.1:${p}/scene/index.html?t=95`);
  console.log("Ctrl+C to stop.");
}
