// RSS dziennika zmian (po polsku, link do wpisu na /zmiany/#id).
import { zmiany } from '../../lib/zmiany';

const SITE = 'https://gitcloud.pl';
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export function GET() {
  const items = zmiany.slice(0, 40).map((z) => `  <item>\n    <title>${esc(z.pl.t)}</title>\n    <link>${SITE}/zmiany/#${z.id}</link>\n    <guid isPermaLink="false">${z.id}</guid>\n    <pubDate>${new Date(z.date + 'T06:00:00Z').toUTCString()}</pubDate>\n    <description>${esc(z.pl.x)}</description>\n  </item>`).join('\n');
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n  <title>GitCloud: zmiany</title>\n  <link>${SITE}/zmiany/</link>\n  <description>Co weszło do systemu GitCloud, noc po nocy.</description>\n  <language>pl</language>\n${items}\n</channel>\n</rss>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/rss+xml' } });
}
