// Kontrola po buildzie: w opublikowanym HTML nie może być nazw klientów/pracodawcy, długich myślników ani prywatnych IP.
// Uruchamiane przez `npm run build`; kod 1 zatrzymuje wdrożenie.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const FORBIDDEN = [
  'staleks', 'laito', 'bestomed', 'bestovet', 'lukoszek', 'mikrosilika', 'wianecka', 'kuriata',
  'łomianki', 'lomianki', 'hornówek', 'hornowek', 'krawczyk',
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
if (errs.length) { console.error(errs.join('\n')); process.exit(1); }
console.log(`check: ok, ${files.length} plików`);
