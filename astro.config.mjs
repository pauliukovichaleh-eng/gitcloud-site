// gitcloud.pl: jednostronicowa wizytówka na Astro (statyczny build → GitHub Pages przez Actions).
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://gitcloud.pl',
  build: { format: 'preserve', inlineStylesheets: 'auto' },
  trailingSlash: 'ignore',
  compressHTML: true,
  devToolbar: { enabled: false },
});
