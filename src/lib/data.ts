import raw from '../data/projects.json';

export type Img = { src: string; alt: string; video?: string; pixelated?: boolean };
export type Project = {
  slug: string; category: 'wlasne' | 'platformy' | 'zlecenia'; title: string; lead: string; year?: string;
  status?: string; image?: string; image_alt?: string; pixelated?: boolean; video?: { src: string; poster: string };
  gallery: Img[]; gallery_note?: string; problem: string; solution: string; stack: string[]; role: string;
  results: string[]; links: { href: string; label: string }[]; links_title?: string; od?: string;
};

// Projekt z polem "od" pokazuje się dopiero od tego dnia (czas Warszawy); workflow przebudowuje stronę codziennie.
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw' }).format(new Date());
const drafts = process.env.GC_DRAFTS === '1';

export const categories = raw.categories as Record<string, string>;
export const projects: Project[] = (raw.projects as Project[]).filter((p) => drafts || !p.od || p.od <= today);
const bySlug = new Map(projects.map((p) => [p.slug, p]));
export const featured: Project[] = raw.featured.map((s: string) => bySlug.get(s)).filter(Boolean) as Project[];
export const rest: Project[] = projects.filter((p) => !raw.featured.includes(p.slug));
export const ordered: Project[] = [...featured, ...rest];
export const has = (slug: string) => bySlug.has(slug);

// Stare adresy /projekty/<slug>/ prowadzą do okna projektu na stronie głównej.
export const anchor = (slug: string) => `p-${slug}`;
export const fixHref = (href: string) => {
  const m = href.match(/^\/projekty\/([a-z0-9-]+)\/?$/);
  if (m) return `#${anchor(m[1])}`;
  if (href === '/isp/') return '#konsola';
  return href;
};
