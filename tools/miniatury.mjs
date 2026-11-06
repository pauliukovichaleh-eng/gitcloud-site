// Lekkie kopie obrazów galerii projektów (uruchamiać ręcznie po dodaniu zdjęć: `node tools/miniatury.mjs`, wynik w repo):
//  - public/img/mini/<nazwa>.webp: miniatura pod galerią, 240 px szerokości (przycisk ma 118 px, ekrany 2x);
//  - public/img/plakat/<nazwa>.webp: pierwszy obraz galerii w 960 px: plakat wideo albo wersja zdjęcia na telefon (srcset);
//    szerokości oryginałów zapisuje w src/data/rozmiary.json (srcset potrzebuje deskryptora w).
// Oryginały zostają (pełny obraz w galerii, og:image, JSON-LD). ProjectBody bierze kopię, jeśli plik istnieje.
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { basename, extname, join } from 'node:path';
import sharp from 'sharp';

const PUB = 'public';
const data = JSON.parse(readFileSync('src/data/projects.json', 'utf8'));
const projects = Array.isArray(data) ? data : data.projects;
const out = { mini: join(PUB, 'img/mini'), plakat: join(PUB, 'img/plakat') };
Object.values(out).forEach((d) => mkdirSync(d, { recursive: true }));

const name = (src) => basename(src, extname(src)) + '.webp';
let n = 0, before = 0, after = 0;
async function make(src, dir, width, quality, px) {
  const from = join(PUB, src), to = join(dir, name(src));
  if (!existsSync(from)) { console.warn(`miniatury: brak ${from}`); return; }
  if (existsSync(to) && statSync(to).mtimeMs >= statSync(from).mtimeMs) return;
  await sharp(from)
    .resize({ width, withoutEnlargement: true, kernel: px ? 'nearest' : 'lanczos3' })
    .webp({ quality, effort: 6, ...(px ? { lossless: true } : {}) })
    .toFile(to);
  n++; before += statSync(from).size; after += statSync(to).size;
}

const sizes = {};
for (const p of projects) {
  for (const [i, g] of (p.gallery || []).entries()) {
    await make(g.src, out.mini, 240, 70, g.pixelated);
    if (i === 0) {
      await make(g.src, out.plakat, 960, 72, g.pixelated);
      if (existsSync(join(PUB, g.src))) sizes[g.src] = (await sharp(join(PUB, g.src)).metadata()).width;
    }
  }
}
writeFileSync('src/data/rozmiary.json', JSON.stringify(sizes, null, 1) + '\n');
console.log(n ? `miniatury: ${n} plików, ${Math.round(before / 1024)} KB → ${Math.round(after / 1024)} KB` : 'miniatury: aktualne');
