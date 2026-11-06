// gitcloud.pl: jednostronicowa wizytówka na Astro (statyczny build → GitHub Pages przez Actions).
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://gitcloud.pl',
  build: { format: 'preserve', inlineStylesheets: 'auto' },
  trailingSlash: 'ignore',
  compressHTML: true,
  devToolbar: { enabled: false },
  // Astro 7 / Vite 8 minifikuje CSS przez Lightning CSS z celem "baseline-widely-available" i zamienia
  // @media(max-width:…) na @media(width<=…), którego Safari < 16.4 nie zna. Cele jak w Vite 6 (Astro 5),
  // żeby CSS dalej działał na starszych iPhone'ach.
  vite: { build: { cssTarget: ['chrome87', 'edge88', 'firefox78', 'safari14'] } },
});
