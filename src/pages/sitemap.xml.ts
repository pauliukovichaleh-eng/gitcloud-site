// sitemap.xml: wizytówka w trzech językach, strony projektów (PL) i polityka prywatności.
// Strony projektów biorą się z projects.json (tylko widoczne, bez aliasów i wycofanych), więc nowy projekt trafia tu sam.
import { projects } from '../lib/data';

const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw' }).format(new Date());
const urls: [string, string, string][] = [
  ['/', 'weekly', '1.0'], ['/en/', 'weekly', '0.9'], ['/ru/', 'weekly', '0.9'],
  ...projects.map((p) => [`/projekty/${p.slug}/`, 'monthly', '0.7'] as [string, string, string]),
  ['/privacy.html', 'yearly', '0.3'],
];
export function GET() {
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls
    .map(([u, f, p]) => `  <url>\n    <loc>https://gitcloud.pl${u}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${f}</changefreq>\n    <priority>${p}</priority>\n  </url>`)
    .join('\n')}\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml' } });
}
