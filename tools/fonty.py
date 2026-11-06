#!/usr/bin/env python3
"""Lekkie fonty strony: podzbiory woff2 z pakietów @fontsource do public/fonts/ + src/styles/fonts.css.

Uruchamiać ręcznie po zmianie pakietów fontów (wymaga fontTools + brotli):
    python3 tools/fonty.py
Co robi:
- Inter Variable (oś wght): podstawowa łacina, polskie litery (osobny mały plik), cyrylica dla /ru/;
  tylko domyślne funkcje OpenType (kern, liga, calt...), bez wariantów ss/cv, które ciągną setki glifów.
- IBM Plex Mono: tylko 400 i 500; plik 500 obsługuje też 600-700 (font-weight: 500 700),
  więc przeglądarka nie dobiera trzeciego pliku i nie pogrubia sztucznie.
- unicode-range każdego pliku to dokładnie to, co w nim jest: przeglądarka pobiera tylko potrzebne pliki,
  a znak spoza podzbioru pokazuje fontem systemowym.
"""
import pathlib, hashlib
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = pathlib.Path(__file__).resolve().parent.parent
NM = ROOT / 'node_modules'
OUT = ROOT / 'public' / 'fonts'
CSS = ROOT / 'src' / 'styles' / 'fonts.css'

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

# Font zapasowy o metrykach Inter / Plex Mono: zanim przyjdzie woff2, tekst ma tę samą szerokość i wysokość,
# więc podmiana fontu nie przesuwa układu (CLS). Wartości policzone 06.11.2026 fontTools: średnia szerokość znaków
# z tekstów strony, Inter (regular i wght 700-800) do Arial / Liberation Sans (zgodne metrycznie), Plex Mono do Courier New.
# size-adjust = szerokość Inter / szerokość Arial; ascent/descent = metryki Inter / size-adjust.
FALLBACK = [
    "@font-face{font-family:'Inter Fallback';font-weight:100 500;src:local('Arial'),local('Liberation Sans'),local('Helvetica');"
    "size-adjust:106.31%;ascent-override:91.13%;descent-override:22.69%;line-gap-override:0%;}",
    "@font-face{font-family:'Inter Fallback';font-weight:600 900;src:local('Arial Bold'),local('Arial-BoldMT'),local('Liberation Sans Bold'),local('Helvetica Bold');"
    "size-adjust:101.6%;ascent-override:95.3%;descent-override:23.7%;line-gap-override:0%;}",
    "@font-face{font-family:'Plex Mono Fallback';src:local('Courier New'),local('CourierNewPSMT'),local('Liberation Mono');"
    "size-adjust:100%;ascent-override:102.5%;descent-override:27.5%;line-gap-override:0%;}",
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
    inter = NM / '@fontsource-variable/inter/files'
    mono = NM / '@fontsource/ibm-plex-mono/files'
    faces = []
    # (rodzina, plik źródłowy, znaki, nazwa, waga css)
    plan = [
        ("'Inter Variable'", inter / 'inter-latin-wght-normal.woff2', LAT, 'inter-lat', '100 900'),
        ("'Inter Variable'", inter / 'inter-latin-ext-wght-normal.woff2', PL, 'inter-pl', '100 900'),
        ("'Inter Variable'", inter / 'inter-cyrillic-wght-normal.woff2', CYR, 'inter-cyr', '100 900'),
    ]
    for w, css_w in (('400', '400'), ('500', '500 700')):
        plan += [
            ("'IBM Plex Mono'", mono / f'ibm-plex-mono-latin-{w}-normal.woff2', LAT, f'plexmono-{w}-lat', css_w),
            ("'IBM Plex Mono'", mono / f'ibm-plex-mono-latin-ext-{w}-normal.woff2', PL, f'plexmono-{w}-pl', css_w),
            ("'IBM Plex Mono'", mono / f'ibm-plex-mono-cyrillic-{w}-normal.woff2', CYR, f'plexmono-{w}-cyr', css_w),
        ]
    css = ['/* Wygenerowane przez tools/fonty.py, nie edytować ręcznie. */']
    for fam, src, cps, name, css_w in plan:
        fn, keep = cut(src, cps, name)
        css.append(f"@font-face{{font-family:{fam};font-style:normal;font-display:swap;font-weight:{css_w};"
                   f"src:url(/fonts/{fn}) format('woff2');unicode-range:{fmt_range(keep)};}}")
    css += FALLBACK
    CSS.write_text('\n'.join(css) + '\n')
    # Bez <link rel=preload>: przy tak małych plikach preload tylko opóźnia pierwsze malowanie (pomiar 06.11.2026).
    print('->', CSS.relative_to(ROOT))

if __name__ == '__main__':
    main()
