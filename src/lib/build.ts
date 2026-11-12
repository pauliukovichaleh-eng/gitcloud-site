// Wersja strony w stopce: krótki hash commita i data budowania.
// W GitHub Actions z GITHUB_SHA, lokalnie z `git rev-parse`; bez gita zostaje "dev".
import { execSync } from 'node:child_process';

const git = (cmd: string) => { try { return execSync(`git ${cmd}`, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch { return ''; } };
const today = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw' }).format(new Date());
// Data ostatniego commita, który zmienił podane pliki (lastmod w sitemap.xml). Wymaga pełnej historii (fetch-depth: 0 w deploy.yml);
// bez gita albo dla plików spoza historii zostaje dzisiejsza data.
export const changed = (...paths: string[]) => git(`log -1 --format=%cs -- ${paths.join(' ')}`) || today;
const sha = process.env.GITHUB_SHA || git('rev-parse HEAD');
export const build = {
  sha,
  short: sha ? sha.slice(0, 7) : 'dev',
  // data i godzina budowania w strefie Warszawy, format 2026-11-06 07:45
  at: new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Warsaw', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date()),
  url: sha ? `https://github.com/pauliukovichaleh-eng/gitcloud-site/commit/${sha}` : '',
};
