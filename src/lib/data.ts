import raw from '../data/projects.json';
import tr from '../data/projects.i18n.json';
import type { Lang } from '../i18n';

export type Img = { src: string; alt: string; video?: string; w?: number; h?: number; pixelated?: boolean; od?: string; i?: number };
export type Stage = { slug: string; title: string; client?: string; od?: string; problem: string; solution: string; results: string[]; stack: string[] };
export type Project = {
  slug: string; category: 'wlasne' | 'platformy' | 'zlecenia'; title: string; lead: string; year?: string;
  status?: string; image?: string; image_alt?: string; pixelated?: boolean; video?: { src: string; poster: string };
  gallery: Img[]; gallery_note?: string; problem: string; solution: string; stack: string[]; role: string;
  results: string[]; links: { href: string; label: string }[]; links_title?: string; od?: string;
  badge?: string; stages?: Stage[]; aliases?: string[];
};

// Projekt z polem "od" pokazuje się dopiero od tego dnia (czas Warszawy); workflow przebudowuje stronę codziennie.
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw' }).format(new Date());
const drafts = process.env.GC_DRAFTS === '1';

export const categories = raw.categories as Record<string, string>;
const visible = (o: { od?: string }) => drafts || !o.od || o.od <= today;
export const projects: Project[] = (raw.projects as Project[]).filter(visible).map((p) => ({
  ...p,
  // i = miejsce w pełnej galerii, żeby gallery_alt z tłumaczeń trafiał w ten sam obraz, gdy część czeka na datę
  gallery: (p.gallery || []).map((g, i) => ({ ...g, i })).filter(visible),
  ...(p.stages ? { stages: p.stages.filter(visible) } : {}),
}));
const bySlug = new Map(projects.map((p) => [p.slug, p]));
// stare slugi połączonych projektów (np. etapy zleceń) → projekt zbiorczy
const alias = new Map(projects.flatMap((p) => (p.aliases || []).map((a) => [a, p.slug] as [string, string])));
export const resolve = (slug: string) => (bySlug.has(slug) ? slug : alias.get(slug));
// liczba realizacji: projekty własne + każdy etap zlecenia osobno
export const deliveries = projects.reduce((n, p) => n + (p.stages?.length || 1), 0);
export const featured: Project[] = raw.featured.map((s: string) => bySlug.get(s)).filter(Boolean) as Project[];
export const rest: Project[] = projects.filter((p) => !raw.featured.includes(p.slug));
export const ordered: Project[] = [...featured, ...rest];
export const has = (slug: string) => bySlug.has(slug);
// stare adresy: projekty, etapy połączone w zbiorczy i projekty wycofane (prowadzą do listy realizacji)
export const allSlugs = [...(raw.projects as Project[]).flatMap((p) => [p.slug, ...(p.aliases || [])]), ...((raw as { retired?: string[] }).retired || [])];

// Stare adresy /projekty/<slug>/ prowadzą do okna projektu na stronie głównej.
export const anchor = (slug: string) => `p-${slug}`;
export const fixHref = (href: string) => {
  const m = href.match(/^\/projekty\/([a-z0-9-]+)\/?$/);
  if (m) { const r = resolve(m[1]); return r ? `#${anchor(r)}` : '#moduly'; }
  if (href === '/isp/') return '#konsola';
  return href;
};

// Wersja projektu w danym języku: pola z projects.i18n.json zastępują polskie, reszta zostaje.
type Tr = Partial<Project> & { gallery_alt?: string[]; links_label?: string[]; stages?: Record<string, Partial<Stage>> };
export const localize = (p: Project, lang: Lang): Project => {
  if (lang === 'pl') return p;
  const o = ((tr as unknown as Record<string, Record<string, Tr>>)[lang] || {})[p.slug];
  if (!o) return p;
  const { gallery_alt, links_label, stages, ...rest } = o;
  return {
    ...p,
    ...rest,
    gallery: (p.gallery || []).map((g, j) => { const i = g.i ?? j; return gallery_alt?.[i] ? { ...g, alt: gallery_alt[i] } : g; }),
    links: (p.links || []).map((l, i) => (links_label?.[i] ? { ...l, label: links_label[i] } : l)),
    stages: p.stages?.map((s) => ({ ...s, ...(stages?.[s.slug] || {}) })),
  } as Project;
};

// Adres strony projektu w danym języku: /projekty/<slug>/ (pl), /en/projekty/<slug>/, /ru/projekty/<slug>/.
export const projectPath = (slug: string, lang: Lang = 'pl') => (lang === 'pl' ? `/projekty/${slug}/` : `/${lang}/projekty/${slug}/`);
