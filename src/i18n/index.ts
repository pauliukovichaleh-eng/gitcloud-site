// Języki strony: pl (główny, /), en (/en/), ru (/ru/). Teksty w pl.ts / en.ts / ru.ts, projekty w data/projects.i18n.json.
import pl from './pl';
import en from './en';
import ru from './ru';

export type Dict = typeof pl;
export type Lang = 'pl' | 'en' | 'ru';
export const LANGS: Lang[] = ['pl', 'en', 'ru'];
export const DICTS: Record<Lang, Dict> = { pl, en, ru };
export const LABEL: Record<Lang, string> = { pl: 'PL', en: 'EN', ru: 'RU' };
export const home = (l: Lang) => (l === 'pl' ? '/' : `/${l}/`);
export const t = (l: Lang): Dict => DICTS[l];
