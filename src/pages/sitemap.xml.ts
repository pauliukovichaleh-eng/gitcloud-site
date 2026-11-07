// sitemap.xml: wizytówka, strony projektów i polityka prywatności w trzech językach (z xhtml:link hreflang), CV (PL, EN).
// Strony projektów biorą się z projects.json (tylko widoczne, bez aliasów i wycofanych), więc nowy projekt trafia tu sam.
import { projects, projectPath } from '../lib/data';
import { LANGS, home, type Lang } from '../i18n';

const SITE = 'https://gitcloud.pl';
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw' }).format(new Date());
type Url = { loc: string; freq: string; prio: string; alt?: Record<Lang, string> };
// grupa: ta sama strona w pl/en/ru, każdy adres wskazuje wszystkie wersje
const group = (paths: Record<Lang, string>, freq: string, prio: (l: Lang) => string): Url[] =>
  LANGS.map((l) => ({ loc: paths[l], freq, prio: prio(l), alt: paths }));
const byLang = (f: (l: Lang) => string) => Object.fromEntries(LANGS.map((l) => [l, f(l)])) as Record<Lang, string>;
const urls: Url[] = [
  ...group(byLang(home), 'weekly', (l) => (l === 'pl' ? '1.0' : '0.9')),
  ...projects.flatMap((p) => group(byLang((l) => projectPath(p.slug, l)), 'monthly', (l) => (l === 'pl' ? '0.7' : '0.6'))),
  { loc: '/cv/', freq: 'monthly', prio: '0.5' }, { loc: '/en/cv/', freq: 'monthly', prio: '0.5' },
  ...group(byLang((l) => (l === 'pl' ? '/zmiany/' : `/${l}/zmiany/`)), 'daily', (l) => (l === 'pl' ? '0.6' : '0.5')),
  ...group(byLang((l) => (l === 'pl' ? '/privacy.html' : `/${l}/privacy.html`)), 'yearly', () => '0.3'),
];
const link = (alt: Record<Lang, string>) =>
  [...LANGS.map((l) => [l, alt[l]]), ['x-default', alt.pl]].map(([h, u]) => `\n    <xhtml:link rel="alternate" hreflang="${h}" href="${SITE}${u}"/>`).join('');
export function GET() {
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls
    .map((u) => `  <url>\n    <loc>${SITE}${u.loc}</loc>${u.alt ? link(u.alt) : ''}\n    <lastmod>${today}</lastmod>\n    <changefreq>${u.freq}</changefreq>\n    <priority>${u.prio}</priority>\n  </url>`)
    .join('\n')}\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml' } });
}
