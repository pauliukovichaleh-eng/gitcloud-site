// Dziennik zmian (decyzja #748): dane src/data/zmiany.json, strony /zmiany/ w trzech językach, RSS /zmiany/rss.xml.
import raw from '../data/zmiany.json';
import type { Lang } from '../i18n';

type Tx = { t: string; x: string };
export type Zmiana = {
  id: string; date: string; area: string; project?: string; kind: 'wizualna' | 'techniczna'; link?: string;
  img?: { src: string; alt?: Partial<Record<Lang, string>>; label?: 'przed' | 'po' | 'kadr' }[];
  pl: Tx; en?: Tx; ru?: Tx;
};
export const zmiany: Zmiana[] = [...(raw.wpisy as Zmiana[])].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
export const zmianyPath = (l: Lang) => (l === 'pl' ? '/zmiany/' : `/${l}/zmiany/`);
export const AREA: Record<string, Record<Lang, string>> = {
  strona: { pl: 'strona', en: 'site', ru: 'сайт' },
  panel: { pl: 'panel', en: 'panel', ru: 'панель' },
  agenci: { pl: 'agenci', en: 'agents', ru: 'агенты' },
  glowy: { pl: 'głowy agentów', en: 'agent heads', ru: 'головы агентов' },
  pilot: { pl: 'pilot ESP32', en: 'ESP32 remote', ru: 'пульт ESP32' },
  isp: { pl: 'konsola ISP', en: 'ISP console', ru: 'консоль ISP' },
  infra: { pl: 'infrastruktura', en: 'infrastructure', ru: 'инфраструктура' },
};
