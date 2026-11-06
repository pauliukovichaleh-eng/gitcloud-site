// Po `astro build`: obrazy og:image (dist/og/<key>.html → dist/img/og/<key>.png) i CV w PDF (dist/cv/…pdf).
// Chrome headless z wiersza poleceń (lokalnie i w GitHub Actions jest google-chrome); dist serwowany na chwilę z 127.0.0.1.
// Bez Chrome: lokalnie ostrzeżenie (GC_NO_RENDER=1 pomija w ogóle), w CI błąd, żeby nie wdrożyć strony bez obrazów i CV.
import { createServer } from 'node:http';
import { execFile } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { extname, join, normalize } from 'node:path';

const DIST = 'dist';
if (process.env.GC_NO_RENDER === '1') { console.log('render: pominięte (GC_NO_RENDER=1)'); process.exit(0); }
const CHROME = [process.env.CHROME, '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find((p) => p && existsSync(p));
if (!CHROME) {
  console[process.env.CI ? 'error' : 'warn']('render: brak Chrome (ustaw CHROME=…)');
  process.exit(process.env.CI ? 1 : 0);
}

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.woff': 'font/woff' };
const server = createServer((req, res) => {
  let p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let f = join(DIST, p);
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html');
  if (!existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[extname(f)] || 'application/octet-stream' });
  res.end(readFileSync(f));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

// Każde uruchomienie z własnym profilem i TMPDIR w katalogu tymczasowym: po zakończeniu nic nie zostaje w /tmp (scoped_dir*).
const work = mkdtempSync(join(tmpdir(), 'gc-render-'));
let n = 0;
const chrome = (args, url) => new Promise((resolve, reject) => {
  const dir = join(work, `p${n++}`); mkdirSync(dir);
  execFile(CHROME, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
    `--user-data-dir=${dir}`, '--virtual-time-budget=4000', ...args, url], { env: { ...process.env, TMPDIR: work }, timeout: 60000 },
  (err, _o, stderr) => (err ? reject(new Error(`${url}: ${err.message}\n${stderr}`)) : resolve()));
});

const jobs = [];
const ogDir = join(DIST, 'og');
if (existsSync(ogDir)) {
  mkdirSync(join(DIST, 'img', 'og'), { recursive: true });
  for (const f of readdirSync(ogDir).filter((x) => x.endsWith('.html'))) {
    const key = f.replace(/\.html$/, '');
    jobs.push(() => chrome(['--window-size=1200,630', `--screenshot=${join(process.cwd(), DIST, 'img', 'og', `${key}.png`)}`], `${base}/og/${f}`).then(() => `og ${key}`));
  }
}
for (const [lang, path] of [['pl', '/cv/'], ['en', '/en/cv/']]) {
  if (!existsSync(join(DIST, path, 'index.html'))) continue;
  jobs.push(() => chrome(['--no-pdf-header-footer', `--print-to-pdf=${join(process.cwd(), DIST, 'cv', `aleh-pauliukovich-cv-${lang}.pdf`)}`], `${base}${path}`).then(() => `cv ${lang}`));
}

// po 3 naraz
const done = [];
let failed = false;
const queue = [...jobs];
await Promise.all(Array.from({ length: 3 }, async () => {
  while (queue.length) {
    const job = queue.shift();
    try { done.push(await job()); } catch (e) { failed = true; console.error(String(e.message || e)); }
  }
}));
server.close();
rmSync(work, { recursive: true, force: true });
rmSync(ogDir, { recursive: true, force: true }); // strony pomocnicze nie idą na serwer
if (failed) process.exit(1);
console.log(`render: ${done.length} plików (${done.join(', ')})`);
