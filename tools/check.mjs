// Kontrola po buildzie: w opublikowanym HTML nie może być nazw klientów/pracodawcy, długich myślników ani prywatnych IP.
// Uruchamiane przez `npm run build`; kod 1 zatrzymuje wdrożenie.
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const FORBIDDEN = [
  'staleks', 'laito', 'bestomed', 'bestovet', 'lukoszek', 'mikrosilika', 'wianecka', 'kuriata',
  'łomianki', 'lomianki', 'hornówek', 'hornowek', 'krawczyk',
  'сталекс', 'лайто', 'kompsystem', 'komp system', 'baltic it',
];
const DASHES = ['—', '–'];
const PRIVATE_IP = /\b(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b/;

const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
const files = walk('dist').filter((f) => /\.(html|xml|json|txt)$/.test(f));
const errs = [];
for (const f of files) {
  const text = readFileSync(f, 'utf8');
  const low = text.toLowerCase();
  for (const w of FORBIDDEN) if (low.includes(w)) errs.push(`${f}: zakazane słowo «${w}»`);
  for (const d of DASHES) if (text.includes(d)) errs.push(`${f}: długi myślnik U+${d.codePointAt(0).toString(16).toUpperCase()}`);
  const m = text.match(PRIVATE_IP); if (m) errs.push(`${f}: prywatny adres IP ${m[0]}`);
}
// Pliki robione przez tools/render.mjs: CV w PDF i karty og:image dla każdej strony, która je wskazuje.
if (process.env.GC_NO_RENDER !== '1') {
  for (const f of ['dist/cv/aleh-pauliukovich-cv-pl.pdf', 'dist/cv/aleh-pauliukovich-cv-en.pdf']) if (!existsSync(f)) errs.push(`brak ${f}`);
  for (const f of files.filter((x) => x.endsWith('.html'))) {
    const m = readFileSync(f, 'utf8').match(/property="og:image" content="https:\/\/gitcloud\.pl(\/img\/og\/[^"]+)"/);
    if (m && !existsSync(join('dist', m[1]))) errs.push(`${f}: brak obrazu og ${m[1]}`);
  }
}
if (errs.length) { console.error(errs.join('\n')); process.exit(1); }
console.log(`check: ok, ${files.length} plików`);

// Kompletność tłumaczeń EN/RU: każdy podpis i tekst z projects.json musi mieć wersję w projects.i18n.json.
const P = JSON.parse(readFileSync('src/data/projects.json', 'utf8'));
const TR = JSON.parse(readFileSync('src/data/projects.i18n.json', 'utf8'));
const FIELDS = ['title', 'lead', 'image_alt', 'status', 'problem', 'solution', 'role', 'results', 'gallery_note', 'links_title'];
const STAGE = ['title', 'client', 'problem', 'solution', 'results'];
const gaps = [];
for (const lang of ['en', 'ru']) for (const p of P.projects) {
  const o = TR[lang]?.[p.slug];
  if (!o) { gaps.push(`${lang}/${p.slug}: brak tłumaczenia`); continue; }
  for (const f of FIELDS) if (p[f] !== undefined && o[f] === undefined) gaps.push(`${lang}/${p.slug}: brak ${f}`);
  const g = (p.gallery || []).length, ga = (o.gallery_alt || []).filter(Boolean).length;
  if (g !== ga) gaps.push(`${lang}/${p.slug}: gallery ${g}, gallery_alt ${ga}`);
  if ((p.links || []).length !== (o.links_label || []).length) gaps.push(`${lang}/${p.slug}: links ≠ links_label`);
  for (const s of p.stages || []) {
    const so = o.stages?.[s.slug];
    if (!so) { gaps.push(`${lang}/${p.slug}/${s.slug}: brak etapu`); continue; }
    for (const f of STAGE) if (s[f] !== undefined && so[f] === undefined) gaps.push(`${lang}/${p.slug}/${s.slug}: brak ${f}`);
  }
}
if (gaps.length) { console.error('Brakujące tłumaczenia:\n' + gaps.join('\n')); process.exit(1); }
console.log('check: tłumaczenia EN/RU kompletne');
