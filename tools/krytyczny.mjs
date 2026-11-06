// Po `astro build` i render.mjs: krytyczny CSS pierwszego ekranu w <style> w każdej stronie, reszta arkusza bez blokowania.
// Chrome headless (DevTools Protocol) otwiera stronę w trzech szerokościach i zaznacza reguły, które trafiają w elementy
// pierwszego ekranu (z zapasem w dół). Reguły wycina się z pliku źródłowego (postcss), więc tekst CSS zostaje taki,
// jak po minifikacji Astro (cele Safari 14, astro.config.mjs). Pełny arkusz dociąga <link rel="preload"> i włącza go po
// pobraniu; bez JS działa <noscript>. Wejście z kotwicą (/#kontakt), odświeżenie i powrót wstecz od razu ładują pełny
// arkusz blokująco (document.write w <head>), bo wtedy pierwszy ekran nie jest górą strony.
// GC_NO_CRITICAL=1 pomija krok. Bez Chrome: lokalnie ostrzeżenie, w CI błąd.
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { extname, join, normalize, relative } from 'node:path';
import postcss from 'postcss';

const DIST = 'dist';
if (process.env.GC_NO_CRITICAL === '1') { console.log('krytyczny: pominięte (GC_NO_CRITICAL=1)'); process.exit(0); }
const CHROME = [process.env.CHROME, '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find((p) => p && existsSync(p));
if (!CHROME) {
  console[process.env.CI ? 'error' : 'warn']('krytyczny: brak Chrome (ustaw CHROME=…)');
  process.exit(process.env.CI ? 1 : 0);
}
// Szerokość × wysokość okna; za pierwszy ekran liczy się FOLD × wysokość (zapas na wyższe telefony i przewinięcie).
const VIEWPORTS = [[390, 844, true], [820, 1180, true], [1350, 940, false]];
const FOLD = 1.3;
// Gdy pierwszy ekran potrzebuje większej części arkusza, zysku nie ma (dłuższy HTML i drugie przeliczenie stylów po
// dociągnięciu arkusza; główna strona: FCP 1,35 → 1,42 s, TBT wyżej) – strona zostaje ze zwykłym <link>.
const MAX_SHARE = 0.4;
const LINK = /<link rel="stylesheet" href="(\/_astro\/[^"]+\.css)">/g;

const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
const pages = walk(DIST).filter((f) => f.endsWith('.html')).map((f) => ({ f, html: readFileSync(f, 'utf8') }))
  .filter((p) => [...p.html.matchAll(LINK)].length === 1)
  .filter((p) => !process.env.GC_CRITICAL_ONLY || p.f.includes(process.env.GC_CRITICAL_ONLY));
if (!pages.length) { console.log('krytyczny: brak stron z arkuszem'); process.exit(0); }

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.mp4': 'video/mp4' };
const server = createServer((req, res) => {
  const p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let f = join(DIST, p);
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html');
  if (!existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[extname(f)] || 'application/octet-stream' });
  res.end(readFileSync(f));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

const work = mkdtempSync(join(tmpdir(), 'gc-critical-'));
const chrome = spawn(CHROME, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  '--mute-audio', '--remote-debugging-port=0', `--user-data-dir=${work}`, 'about:blank'], { env: { ...process.env, TMPDIR: work }, stdio: 'ignore', detached: true });
const exited = new Promise((r) => chrome.on('exit', r));
const finish = async (code) => {
  try { process.kill(-chrome.pid, 'SIGKILL'); } catch {} // google-chrome to skrypt: cała grupa procesów
  await Promise.race([exited, new Promise((r) => setTimeout(r, 3000))]);
  server.close(); rmSync(work, { recursive: true, force: true, maxRetries: 5 }); process.exit(code);
};

let port;
for (let i = 0; i < 100 && !port; i++) {
  const f = join(work, 'DevToolsActivePort');
  if (existsSync(f)) port = readFileSync(f, 'utf8').split('\n')[0];
  else await new Promise((r) => setTimeout(r, 100));
}
if (!port) { console.error('krytyczny: Chrome nie wystartował'); await finish(1); }

// Jedna karta, prosty klient CDP.
const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let seq = 0; const waiting = new Map(); const listeners = [];
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && waiting.has(d.id)) { const [r, j] = waiting.get(d.id); waiting.delete(d.id); d.error ? j(new Error(d.error.message)) : r(d.result); }
  else if (d.method) listeners.forEach((l) => l(d));
};
const send = (method, params = {}) => new Promise((r, j) => { const id = ++seq; waiting.set(id, [r, j]); ws.send(JSON.stringify({ id, method, params })); });
const once = (method) => new Promise((r) => { const l = (d) => { if (d.method === method) { listeners.splice(listeners.indexOf(l), 1); r(d); } }; listeners.push(l); });
await send('Page.enable');

// W stronie: drzewo reguł arkusza (liczby dzieci, do sprawdzenia zgodności z postcss) i ścieżki reguł pierwszego ekranu.
const PROBE = (href, fold) => `(async () => {
  await document.fonts.ready; await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sheet = [...document.styleSheets].find((s) => s.href && new URL(s.href).pathname === ${JSON.stringify(href)});
  if (!sheet) return { error: 'brak arkusza' };
  const H = innerHeight * ${fold};
  const DYN = /::?(?:hover|focus-visible|focus-within|focus|active|visited|link|target|before|after|placeholder|selection|marker|first-letter|first-line|backdrop|-webkit-[a-z-]+|-moz-[a-z-]+)(?![\\w-])/g;
  const above = (sel) => {
    const s = sel.replace(DYN, '').trim() || '*';
    let els; try { els = document.querySelectorAll(s); } catch { return true; }
    for (const e of els) { const r = e.getBoundingClientRect(); if (r.top < H) return true; }
    return false;
  };
  const tree = (rules) => [...rules].map((r) => {
    if (r instanceof CSSStyleRule) return { s: r.selectorText, k: r.selectorText.split(/,(?![^(]*\\))/).some(above) };
    if (r.cssRules && !(r instanceof CSSKeyframesRule)) return { g: tree(r.cssRules) };
    return { o: 1 };
  });
  return { tree: tree(sheet.cssRules) };
})()`;

// Suma z kilku szerokości: reguła zostaje, jeśli trafiła w pierwszy ekran choć raz.
const merge = (a, b) => (a ? a.map((x, i) => (x.g ? { g: merge(x.g, b[i].g) } : x.s !== undefined ? { s: x.s, k: x.k || b[i].k } : x)) : b);
let failed = false;
for (const p of pages) {
  const href = [...p.html.matchAll(LINK)][0][1];
  const url = `${base}/${relative(DIST, p.f).replace(/index\.html$/, '')}`;
  let tree, ok = true;
  for (const [w, h, mobile] of VIEWPORTS) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile });
    const loaded = once('Page.loadEventFired');
    await send('Page.navigate', { url });
    await Promise.race([loaded, new Promise((r) => setTimeout(r, 15000))]);
    const { result, exceptionDetails } = await send('Runtime.evaluate', { expression: PROBE(href, FOLD), awaitPromise: true, returnByValue: true });
    if (exceptionDetails || result.value?.error) { console.error(`krytyczny: ${p.f}: ${result.value?.error || exceptionDetails.text}`); failed = true; ok = false; break; }
    tree = merge(tree, result.value.tree);
  }
  p.href = href; p.tree = ok && tree; // niepełny pomiar = strona bez zmian
}

// CSSOM ↔ postcss po kolei: reguły, których Chrome nie zna (np. :-moz-any(…)), są w postcss, a w CSSOM ich nie ma.
// Takie zostają w krytycznym CSS (to drobne odpowiedniki dla innych przeglądarek). Każda inna rozbieżność = błąd.
const roots = new Map();
const GROUP = /^(?:media|supports|container|layer|scope|starting-style)$/;
const nodes = (n) => (n.nodes || []).filter((c) => c.type === 'rule' || c.type === 'atrule');
const norm = (sel) => sel.replace(/\s+/g, '').replace(/["'\\]/g, '').toLowerCase()
  .replace(/(^|[^:]):(before|after|first-line|first-letter)/g, '$1::$2');
const prune = (n, items, stat) => {
  let j = 0;
  for (const c of nodes(n)) {
    const it = items[j];
    if (c.type === 'rule') {
      if (it && it.s !== undefined && norm(it.s) === norm(c.selector)) { j++; if (!it.k) c.remove(); }
      else { stat.unknown++; if (process.env.GC_CRITICAL_VERBOSE && stat.unknown < 4) console.log('  ?', c.selector, '≠', it && (it.s || JSON.stringify(it).slice(0, 80))); }
    } else if (GROUP.test(c.name)) {
      if (it && it.g) { j++; prune(c, it.g, stat); if (!nodes(c).length) c.remove(); }
      else stat.unknown++;
    } else if (it && it.o) j++;
    else stat.unknown++;
  }
  if (j !== items.length) stat.bad = true;
};
const out = []; const skipped = [];
for (const p of pages) {
  if (!p.tree) continue;
  if (!roots.has(p.href)) roots.set(p.href, postcss.parse(readFileSync(join(DIST, p.href), 'utf8')));
  // Zostają: reguły pierwszego ekranu, @font-face itp., @keyframes użyte w zostawionych regułach.
  const crit = roots.get(p.href).clone();
  const stat = { unknown: 0, bad: false };
  prune(crit, p.tree, stat);
  if (stat.bad || stat.unknown > 20) { console.error(`krytyczny: ${p.f}: CSSOM ≠ postcss (nieznanych reguł ${stat.unknown}), strona bez zmian`); failed = true; continue; }
  crit.walkComments((c) => c.remove());
  const used = crit.toString();
  crit.walkAtRules(/keyframes$/, (a) => { if (!new RegExp(`\\b${a.params.replace(/[^\w-]/g, '')}\\b`).test(used.replace(a.toString(), ''))) a.remove(); });
  const css = crit.toString().replace(/<\/style/gi, '<\\/style');
  const share = css.length / roots.get(p.href).toString().length;
  if (share > MAX_SHARE) { skipped.push(`${relative(DIST, p.f)} ${Math.round(share * 100)}%`); continue; }
  const h = p.href;
  const tag = `<style>${css}</style><link rel="preload" href="${h}" as="style" onload="this.onload=null;this.rel='stylesheet'">`
    + `<noscript><link rel="stylesheet" href="${h}"></noscript>`
    + `<script>(function(){var n=performance.getEntriesByType&&performance.getEntriesByType('navigation')[0];`
    + `if(location.hash||(n&&n.type!=='navigate')){document.write('<link rel="stylesheet" href="${h}">');`
    + `var l=document.querySelector('link[rel=preload][as=style]');if(l)l.onload=null}})()</script>`;
  writeFileSync(p.f, p.html.replace(LINK, () => tag));
  out.push([relative(DIST, p.f), css.length, stat.unknown]);
}
const full = Math.max(...[...roots.values()].map((r) => r.toString().length));
const avg = out.length ? Math.round(out.reduce((s, [, n]) => s + n, 0) / out.length / 1024) : 0;
console.log(`krytyczny: ${out.length} stron, w <style> średnio ${avg} KB z ${Math.round(full / 1024)} KB arkusza`
  + (skipped.length ? `; bez zmian (pierwszy ekran > ${MAX_SHARE * 100}% arkusza): ${skipped.join(', ')}` : ''));
if (process.env.GC_CRITICAL_VERBOSE) out.forEach(([f, n, u]) => console.log(`  ${f} ${(n / 1024).toFixed(1)} KB (spoza Chrome: ${u})`));
await finish(failed ? 1 : 0);
