// Po `astro build` i render.mjs: krytyczny CSS pierwszego ekranu w <style> w każdej stronie, reszta arkusza bez blokowania.
// Chrome headless (DevTools Protocol) otwiera stronę w trzech szerokościach i zaznacza reguły, które trafiają w elementy
// pierwszego ekranu (z zapasem w dół). Reguły wycina się z pliku źródłowego (postcss), więc tekst CSS zostaje taki,
// jak po minifikacji Astro (cele Safari 14, astro.config.mjs). Pełny arkusz dociąga <link rel="preload"> i włącza go po
// pobraniu; bez JS działa <noscript>. Wejście z kotwicą (/#kontakt), odświeżenie i powrót wstecz od razu ładują pełny
// arkusz blokująco (document.write w <head>), bo wtedy pierwszy ekran nie jest górą strony.
// Przy okazji tego samego pomiaru: strażnik wysokości zastępczych (contain-intrinsic-size sekcji z content-visibility:auto,
// site.css). Trzy szerokości tu = trzy zestawy wysokości tam (do 620 / do 980 / szerzej). Po nowym projekcie albo wierszu
// treść rośnie, a liczba w CSS nie; rozjazd > CV_TOL to ostrzeżenie (w CI adnotacja ::warning::), build idzie dalej.
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
const CV_TOL = 0.15; // strażnik wysokości: dopuszczalny rozjazd wysokości zastępczej względem prawdziwej
// Gdy pierwszy ekran potrzebuje większej części arkusza, zysku nie ma (dłuższy HTML i drugie przeliczenie stylów po
// dociągnięciu arkusza) – strona zostaje ze zwykłym <link>. Główna PL/EN/RU po pominięciu ukrytych okien: ~31%.
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
const chrome = spawn(CHROME, ['--headless=new', '--password-store=basic', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  '--mute-audio', '--remote-debugging-port=0', `--user-data-dir=${work}`, 'about:blank'], { env: { ...process.env, TMPDIR: work }, stdio: 'ignore', detached: true });
const exited = new Promise((r) => chrome.on('exit', r));
const killChrome = () => { try { process.kill(-chrome.pid, 'SIGKILL'); } catch {} }; // google-chrome to skrypt: cała grupa procesów
let finishing = false;
const finish = async (code) => {
  if (finishing) return;
  finishing = true;
  killChrome();
  await Promise.race([exited, new Promise((r) => setTimeout(r, 3000))]);
  server.close(); rmSync(work, { recursive: true, force: true, maxRetries: 5 }); process.exit(code);
};
// Chrome jest detached: przerwany build (Ctrl+C, timeout, usunięty worktree) albo wyjątek zostawiały go żywego na
// zawsze (10.11.2026: 4 sieroty, ~30% rdzenia przez dobę). Każde wyjście z procesu gasi grupę Chrome.
process.on('exit', killChrome);
for (const s of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(s, () => { console.error(`krytyczny: ${s}, sprzątam Chrome`); finish(1); });
// Strony zapisuje się dopiero po pomiarze wszystkich, więc przerwanie zostawia dist bez zmian (zwykły <link>).
// Jak przy braku Chrome: lokalnie ostrzeżenie i build idzie dalej, w CI błąd.
const giveUp = (why) => { console[process.env.CI ? 'error' : 'warn'](`krytyczny: ${why}; strony bez zmian`); finish(process.env.CI ? 1 : 0); };
process.on('uncaughtException', (e) => giveUp(e.message || e));
process.on('unhandledRejection', (e) => giveUp(e?.message || e));
setTimeout(() => giveUp('limit 15 min'), 15 * 60_000).unref();

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
// 10.11.2026: na hoście renderer potrafi zawisnąć na pierwszej stronie i nie odpowiada nawet na document.readyState;
// bez limitu skrypt czekał wiecznie, a przerwany build zostawiał Chrome. Brak odpowiedzi = jak brak Chrome.
const SEND_MS = 30_000;
const send = (method, params = {}) => new Promise((r, j) => {
  const id = ++seq;
  const t = setTimeout(() => { waiting.delete(id); j(new Error(`Chrome nie odpowiada na ${method} od ${SEND_MS / 1000} s`)); }, SEND_MS);
  waiting.set(id, [(v) => { clearTimeout(t); r(v); }, (e) => { clearTimeout(t); j(e); }]);
  ws.send(JSON.stringify({ id, method, params }));
});
const once = (method) => new Promise((r) => { const l = (d) => { if (d.method === method) { listeners.splice(listeners.indexOf(l), 1); r(d); } }; listeners.push(l); });
await send('Page.enable');

// W stronie: drzewo reguł arkusza (liczby dzieci, do sprawdzenia zgodności z postcss) i ścieżki reguł pierwszego ekranu.
const PROBE = (href, fold) => `(async () => {
  await document.fonts.ready; await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sheet = [...document.styleSheets].find((s) => s.href && new URL(s.href).pathname === ${JSON.stringify(href)});
  if (!sheet) return { error: 'brak arkusza' };
  const H = innerHeight * ${fold};
  const DYN = /::?(?:hover|focus-visible|focus-within|focus|active|visited|link|target|before|after|placeholder|selection|marker|first-letter|first-line|backdrop|-webkit-[a-z-]+|-moz-[a-z-]+)(?![\\w-])/g;
  // Element niewyrenderowany (display:none, zamknięty <dialog>, [hidden]) ma prostokąt 0×0 w (0,0), czyli „nad linią”.
  // Liczy się tylko korzeń ukrytego poddrzewa i tylko reguła z display (może go ukrywać); jego wnętrze nie.
  const shown = (e) => e.getClientRects().length > 0 || getComputedStyle(e).display === 'contents';
  const above = (sel, rule) => {
    const s = sel.replace(DYN, '').trim() || '*';
    let els; try { els = document.querySelectorAll(s); } catch { return true; }
    for (const e of els) {
      if (e.getBoundingClientRect().top >= H) continue;
      if (shown(e)) return true;
      if (rule.style.display && (!e.parentElement || shown(e.parentElement))) return true;
    }
    return false;
  };
  const tree = (rules) => [...rules].map((r) => {
    if (r instanceof CSSStyleRule) return { s: r.selectorText, k: r.selectorText.split(/,(?![^(]*\\))/).some((x) => above(x, r)) };
    if (r.cssRules && !(r instanceof CSSKeyframesRule)) return { g: tree(r.cssRules) };
    return { o: 1 };
  });
  const rules = tree(sheet.cssRules);
  // Wysokość zastępcza (computed contain-intrinsic-height, np. "auto 610px") i prawdziwa wysokość treści tej samej sekcji:
  // html.cv-off układa wszystko od razu; treść = clientHeight bez paddingu (tak mierzono liczby w site.css).
  const secs = [...document.querySelectorAll('section[id]')].filter((e) => getComputedStyle(e).contentVisibility === 'auto')
    .map((e) => ({ e, id: e.id, decl: parseFloat(getComputedStyle(e).containIntrinsicHeight.replace('auto', '')) }))
    .filter((x) => x.decl > 0);
  let cv = [];
  if (secs.length) {
    const root = document.documentElement, had = root.classList.contains('cv-off');
    root.classList.add('cv-off');
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    cv = secs.map(({ e, id, decl }) => { const st = getComputedStyle(e);
      return { id, decl, real: Math.round(e.clientHeight - parseFloat(st.paddingTop) - parseFloat(st.paddingBottom)) }; });
    if (!had) root.classList.remove('cv-off');
  }
  return { tree: rules, cv };
})()`;

// Suma z kilku szerokości: reguła zostaje, jeśli trafiła w pierwszy ekran choć raz.
const merge = (a, b) => (a ? a.map((x, i) => (x.g ? { g: merge(x.g, b[i].g) } : x.s !== undefined ? { s: x.s, k: x.k || b[i].k } : x)) : b);
let failed = false;
const cvWarn = []; let cvCount = 0;
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
    for (const { id, decl, real } of result.value.cv) {
      cvCount++;
      if (real > 0 && Math.abs(decl - real) / real > CV_TOL) cvWarn.push(`${relative(DIST, p.f)} ${w}px #${id}: ${decl} → ${real} px (${real > decl ? '+' : ''}${Math.round((real - decl) / decl * 100)}%)`);
    }
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
if (cvWarn.length) {
  const msg = `wysokości zastępcze w site.css nieaktualne (> ${CV_TOL * 100}%, zmierzyć ponownie):`;
  if (process.env.CI) cvWarn.forEach((x) => console.log(`::warning title=krytyczny: wysokości zastępcze::${x}`));
  console.warn(`krytyczny: ${msg}\n  ${cvWarn.join('\n  ')}`);
} else if (cvCount) console.log(`krytyczny: wysokości zastępcze ok (${cvCount} pomiarów, rozjazd ≤ ${CV_TOL * 100}%)`);
if (process.env.GC_CRITICAL_VERBOSE) out.forEach(([f, n, u]) => console.log(`  ${f} ${(n / 1024).toFixed(1)} KB (spoza Chrome: ${u})`));
await finish(failed ? 1 : 0);
