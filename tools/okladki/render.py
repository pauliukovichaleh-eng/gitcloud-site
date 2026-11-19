"""Ilustracje zleceń: makiety na danych przykładowych -> img/projekty/zl-*.jpg (1280x720).
Okładka (pierwsza w NAMES[...]) dostaje też *-karta.jpg (640x360); reszta to galeria strony projektu.
Schematy (GALERIA) mają okładkę webp zrobioną wcześniej, tu tylko obrazy galerii, bez karty.
Uruchom: ~/job-hunter/.venv/bin/python -I tools/okladki/render.py [koszyk seo ...]  (Playwright + google-chrome)"""
import pathlib, subprocess, sys
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent.parent / "public" / "img" / "projekty"
NAMES = {
    "koszyk": [("koszyk", "zl-koszyk"), ("koszyk-przed", "zl-koszyk-przed"), ("koszyk-skrypt", "zl-koszyk-skrypt")],
    "seo": [("seo", "zl-seo"), ("seo-meta", "zl-seo-meta"), ("seo-tagi", "zl-seo-tagi")],
    "wybor": [("wybor", "zl-wybor-kraju"), ("wybor-przed", "zl-wybor-kraju-przed"), ("wybor-tel", "zl-wybor-kraju-tel")],
    "tlumaczenie": [("tlumaczenie", "zl-tlumaczenie"), ("tlumaczenie-przed", "zl-tlumaczenie-przed"),
                    ("tlumaczenie-frazy", "zl-tlumaczenie-frazy")],
    "b2b": [("b2b", "zl-baza-b2b"), ("b2b-raport", "zl-baza-b2b-raport"), ("b2b-wiadomosci", "zl-baza-b2b-wiadomosci")],
}
GALERIA = {
    "rdzen": [("rdzen-serwis", "rdzen-serwis"), ("rdzen-tokeny", "rdzen-tokeny"), ("rdzen-szyna", "rdzen-szyna")],
    "pracodawca": [("pracodawca-dostep", "pracodawca-dostep"), ("pracodawca-przeglad", "pracodawca-przeglad")],
}
only = set(sys.argv[1:])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    for key, pages in {**NAMES, **GALERIA}.items():
        if only and key not in only: continue
        for i, (src, dst) in enumerate(pages):
            pg.goto((HERE / f"{src}.html").as_uri()); pg.wait_for_timeout(300)
            big = OUT / f"{dst}.jpg"
            pg.screenshot(path=str(big), type="jpeg", quality=82)
            if i == 0 and key in NAMES:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(big), "-vf", "scale=640:360", "-q:v", "4",
                                str(OUT / f"{dst}-karta.jpg")], check=True)
            print(dst)
    b.close()
