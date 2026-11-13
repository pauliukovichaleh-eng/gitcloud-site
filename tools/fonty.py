#!/usr/bin/env python3
"""Lekkie fonty strony: podzbiory woff2 z pakietów @fontsource do public/fonts/ + src/styles/fonts.css.

Uruchamiać ręcznie po zmianie pakietów fontów (wymaga fontTools + brotli):
    python3 tools/fonty.py
Co robi:
- (do 07.11.2026 Inter i IBM Plex Mono; teraz Onest i JetBrains Mono jak panel) Inter Variable (oś wght): podstawowa łacina, polskie litery (osobny mały plik), cyrylica dla /ru/;
  tylko domyślne funkcje OpenType (kern, liga, calt...), bez wariantów ss/cv, które ciągną setki glifów.
- IBM Plex Mono: tylko 400 i 500; plik 500 obsługuje też 600-700 (font-weight: 500 700),
  więc przeglądarka nie dobiera trzeciego pliku i nie pogrubia sztucznie.
- unicode-range każdego pliku to dokładnie to, co w nim jest: przeglądarka pobiera tylko potrzebne pliki,
  a znak spoza podzbioru pokazuje fontem systemowym.
"""
import pathlib, hashlib, json
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = pathlib.Path(__file__).resolve().parent.parent
NM = ROOT / 'node_modules'
OUT = ROOT / 'public' / 'fonts'
CSS = ROOT / 'src' / 'styles' / 'fonts.css'
PRELOAD = ROOT / 'src' / 'data' / 'fonty.json'  # Base.astro: <link rel=preload> kroju tekstu dla języka strony

def rng(*parts):
    cps = set()
    for p in parts:
        if isinstance(p, tuple): cps.update(range(p[0], p[1] + 1))
        elif isinstance(p, str): cps.update(ord(c) for c in p)
        else: cps.add(p)
    return cps

# Łacina: ASCII, Latin-1, typografia i strzałki używane na stronie
LAT = rng((0x20, 0x7E), (0xA0, 0xFF), (0x2010, 0x2027), (0x2030, 0x203A), 0x2044, 0x20AC, 0x2122,
          (0x2190, 0x2193), 0x2197, 0x2212, 0x2215, 0xFFFD)
PL = rng('ĄąĆćĘęŁłŃńŚśŹźŻż')
CYR = rng((0x400, 0x45F), 0x490, 0x491, 0x2116)

# Font zapasowy o metrykach Onest / JetBrains Mono: zanim przyjdzie woff2, tekst ma prawie tę samą szerokość i wysokość,
# więc podmiana fontu nie przesuwa układu (CLS). Pomiar 13.11.2026: size-adjust = mediana stosunku szerokości Onest do
# Liberation Sans (metrycznie = Arial) na nagłówkach, przyciskach i akapitach głównej PL/EN/RU, osobno dla wagi 400, 600,
# 700 i 800 (jedna wartość na 600 do 900 łamała tytuł hero inaczej niż Onest: na ekranie 1280 px tekst skakał o 62 px).
# ascent/descent = metryki Onest (970 / 305 na 1000) / size-adjust; JetBrains Mono (1020 / 300) do Liberation Mono 1:1.
FALLBACK = [
    "@font-face{font-family:'Onest Fallback';font-weight:100 500;src:local('Arial'),local('Liberation Sans'),local('Helvetica');"
    "size-adjust:106.4%;ascent-override:91.17%;descent-override:28.67%;line-gap-override:0%;}",
    "@font-face{font-family:'Onest Fallback';font-weight:600;src:local('Arial Bold'),local('Arial-BoldMT'),local('Liberation Sans Bold'),local('Helvetica Bold');"
    "size-adjust:98.0%;ascent-override:98.98%;descent-override:31.12%;line-gap-override:0%;}",
    "@font-face{font-family:'Onest Fallback';font-weight:700;src:local('Arial Bold'),local('Arial-BoldMT'),local('Liberation Sans Bold'),local('Helvetica Bold');"
    "size-adjust:99.7%;ascent-override:97.29%;descent-override:30.59%;line-gap-override:0%;}",
    "@font-face{font-family:'Onest Fallback';font-weight:800 900;src:local('Arial Bold'),local('Arial-BoldMT'),local('Liberation Sans Bold'),local('Helvetica Bold');"
    "size-adjust:102.3%;ascent-override:94.82%;descent-override:29.81%;line-gap-override:0%;}",
    "@font-face{font-family:'Mono Fallback';src:local('Courier New'),local('CourierNewPSMT'),local('Liberation Mono');"
    "size-adjust:100%;ascent-override:102%;descent-override:30%;line-gap-override:0%;}",
]

def fmt_range(cps):
    cps = sorted(cps); out = []; a = b = cps[0]
    for c in cps[1:]:
        if c == b + 1: b = c; continue
        out.append((a, b)); a = b = c
    out.append((a, b))
    return ', '.join(f'U+{x:X}' if x == y else f'U+{x:X}-{y:X}' for x, y in out)

def cut(src, cps, name):
    font = TTFont(src, recalcTimestamp=False)  # stała data: ten sam wynik = ta sama nazwa pliku
    have = set(font.getBestCmap())
    keep = cps & have
    opt = subset.Options()
    opt.flavor = 'woff2'
    opt.layout_features = ['kern', 'liga', 'calt', 'ccmp', 'locl', 'mark', 'mkmk', 'rlig', 'rvrn']
    opt.name_IDs = [0, 1, 2, 3, 4, 6, 13, 14]   # prawa autorskie i licencja OFL zostają w pliku
    opt.notdef_outline = True
    opt.hinting = False
    opt.desubroutinize = True
    s = subset.Subsetter(opt); s.populate(unicodes=keep); s.subset(font)
    tmp = OUT / f'{name}.woff2'
    font.flavor = 'woff2'; font.save(tmp)
    h = hashlib.sha1(tmp.read_bytes()).hexdigest()[:8]
    dst = OUT / f'{name}.{h}.woff2'; tmp.rename(dst)
    print(f'{dst.name:34} {dst.stat().st_size/1024:6.1f} KB  ({src.stat().st_size/1024:.1f} KB źródło, {len(keep)} znaków)')
    return dst.name, keep

def main():
    for f in OUT.glob('*.woff2'): f.unlink()
    # 07.11.2026 (decyzja #679 «jedna ekosystema»): kroje jak panel my.gitcloud.pl — Onest (tekst) i JetBrains Mono (cyfry),
    # oba zmienne (oś wght), więc jeden plik na zakres znaków
    onest = NM / '@fontsource-variable/onest/files'
    mono = NM / '@fontsource-variable/jetbrains-mono/files'
    faces = []
    # (rodzina, plik źródłowy, znaki, nazwa, waga css)
    plan = [
        ("'Onest Variable'", onest / 'onest-latin-wght-normal.woff2', LAT, 'onest-lat', '100 900'),
        ("'Onest Variable'", onest / 'onest-latin-ext-wght-normal.woff2', PL, 'onest-pl', '100 900'),
        ("'Onest Variable'", onest / 'onest-cyrillic-wght-normal.woff2', CYR, 'onest-cyr', '100 900'),
        ("'JetBrains Mono Variable'", mono / 'jetbrains-mono-latin-wght-normal.woff2', LAT, 'jbmono-lat', '100 800'),
        ("'JetBrains Mono Variable'", mono / 'jetbrains-mono-latin-ext-wght-normal.woff2', PL, 'jbmono-pl', '100 800'),
        ("'JetBrains Mono Variable'", mono / 'jetbrains-mono-cyrillic-wght-normal.woff2', CYR, 'jbmono-cyr', '100 800'),
    ]
    css = ['/* Wygenerowane przez tools/fonty.py, nie edytować ręcznie. */']
    files = {}
    for fam, src, cps, name, css_w in plan:
        fn, keep = cut(src, cps, name)
        files[name] = f'/fonts/{fn}'
        css.append(f"@font-face{{font-family:{fam};font-style:normal;font-display:swap;font-weight:{css_w};"
                   f"src:url(/fonts/{fn}) format('woff2');unicode-range:{fmt_range(keep)};}}")
    css += FALLBACK
    CSS.write_text('\n'.join(css) + '\n')
    # Onest przed pierwszą odrysowką (okres blokady swap ~100 ms): bez podmiany fontu tytuł hero nie zmienia łamania
    PRELOAD.write_text(json.dumps({'pl': [files['onest-lat'], files['onest-pl']], 'en': [files['onest-lat']],
                                   'ru': [files['onest-lat'], files['onest-cyr']]}, indent=2) + '\n')
    # Bez <link rel=preload>: przy tak małych plikach preload tylko opóźnia pierwsze malowanie (pomiar 06.11.2026).
    print('->', CSS.relative_to(ROOT))

if __name__ == '__main__':
    main()
