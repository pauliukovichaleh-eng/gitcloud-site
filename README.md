# gitcloud.pl

Jednostronicowa wizytówka ekosystemu GitCloud. Astro (statyczny build), wdrożenie na GitHub Pages przez `.github/workflows/deploy.yml`.

- `src/pages/index.astro` – cała strona: ekosystem, architektura, moduły, konsola ISP, agenci, usługi, operator, kontakt
- `src/data/projects.json` – katalog projektów (okna `#p-<slug>`); pole `od` ukrywa projekt do daty
- `src/styles/site.css` – paleta motywu „Kolor” konsoli GitCloud
- `public/` – pliki 1:1 (CNAME, favicony, obrazy; zrzuty konsoli w `img/demo/` z wersji demo)
- stare adresy `/projekty/…`, `/uslugi/`, `/isp/` przekierowują do sekcji strony
- `tools/check.mjs` – po buildzie: zakazane nazwy, długie myślniki, prywatne IP

```
npm ci
npm run dev      # podgląd
npm run build    # dist/ + kontrola
GC_DRAFTS=1 npm run build   # razem z projektami przed datą "od"
```

## Języki
- `/` polski, `/en/` angielski, `/ru/` rosyjski: jeden szablon `src/components/Home.astro`, teksty w `src/i18n/{pl,en,ru}.ts`
- projekty: polski w `src/data/projects.json`, tłumaczenia w `src/data/projects.i18n.json` (brakujące pole zostaje po polsku)
- nowe teksty bez długich myślników i bez nazw pracodawców (sprawdza `tools/check.mjs`)
