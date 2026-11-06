# gitcloud.pl

Jednostronicowa wizytówka ekosystemu GitCloud. Astro (statyczny build), wdrożenie na GitHub Pages przez `.github/workflows/deploy.yml`.

- `src/components/Home.astro` – cała strona: ekosystem, żywa architektura (powiązania warstw), realizacje, konsola ISP z punktami na zrzutach, agenci, usługi, doświadczenie, kontakt
- `src/data/projects.json` – katalog projektów (okna `#p-<slug>`); pole `od` ukrywa projekt do daty
- `src/styles/site.css` – paleta motywu „Kolor” konsoli GitCloud
- `public/` – pliki 1:1 (CNAME, favicony, obrazy; zrzuty konsoli w `img/demo/` z wersji demo)
- stare adresy `/projekty/…`, `/uslugi/`, `/isp/` przekierowują do sekcji strony
- `tools/render.mjs` – po buildzie (Chrome headless): karty og:image `dist/img/og/<klucz>.png` ze stron `src/pages/og/[key].astro` i CV w PDF `dist/cv/aleh-pauliukovich-cv-{pl,en}.pdf` ze stron `/cv/`, `/en/cv/`; `GC_NO_RENDER=1` pomija
- `tools/krytyczny.mjs` – po render.mjs (Chrome headless, DevTools Protocol): każda strona otwarta w 390, 820 i 1350 px, reguły CSS trafiające w pierwszy ekran (×1,3 wysokości) idą do `<style>` w `<head>` (wycięte z pliku źródłowego przez postcss, kolejność i cele Safari 14 bez zmian), pełny arkusz przez `<link rel="preload">` bez blokowania, `<noscript>` dla stron bez JS; wejście z kotwicą (`/#kontakt`), odświeżenie i powrót wstecz ładują pełny arkusz blokująco, bo pierwszym ekranem nie jest góra strony. Strona, której pierwszy ekran potrzebuje > 40% arkusza (główna PL/EN/RU), zostaje ze zwykłym `<link>` (bez zysku). `GC_NO_CRITICAL=1` pomija, `GC_CRITICAL_VERBOSE=1` pokazuje rozmiar na stronę
- `tools/miniatury.mjs` – ręcznie po dodaniu zdjęć do galerii: miniatury 240 px `public/img/mini/`, pierwszy obraz galerii 960 px `public/img/plakat/` (plakat wideo, srcset na telefon), szerokości w `src/data/rozmiary.json`; wynik w repo
- `tools/fonty.py` – ręcznie po aktualizacji pakietów `@fontsource*` (Python + fontTools, brotli): podzbiory woff2 w `public/fonts/` (Inter: łacina, polskie litery, cyrylica; IBM Plex Mono tylko 400 i 500, plik 500 obsługuje też 600–700), `@font-face` w `src/styles/fonts.css`; bez preload (małe pliki, preload opóźniał pierwsze malowanie); wynik w repo. Znak spoza podzbioru pokazuje się fontem systemowym – nowy znak w tekstach dopisać do zakresu w skrypcie
- `tools/check.mjs` – po buildzie: zakazane nazwy, długie myślniki, prywatne IP, obecność PDF i obrazów og
- `src/data/stats.json` – liczby w pasku KPI; commity odświeża `tools/stats.sh` (lokalnie, liczy repozytoria GitCloud w ~/src)
- paleta poleceń Ctrl+K (`src/components/Palette.astro`), wersja w stopce (`src/lib/build.ts`, hash z `GITHUB_SHA` lub gita), `404.astro` w trzech językach
- `.github/workflows/lighthouse.yml` + `lighthouserc.json` – Lighthouse CI po każdym pushu, nie blokuje wdrożenia

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
