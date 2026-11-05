"""Okładki zleceń: makiety na danych przykładowych -> img/projekty/zl-*.jpg (1280x720) i *-karta.jpg (640x360).
Uruchom: ~/job-hunter/.venv/bin/python -I tools/okladki/render.py  (Playwright + google-chrome)"""
import pathlib, subprocess
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent.parent / "public" / "img" / "projekty"
NAMES = {"koszyk": "zl-koszyk", "seo": "zl-seo", "wybor": "zl-wybor-kraju", "tlumaczenie": "zl-tlumaczenie", "b2b": "zl-baza-b2b"}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    import sys
    only = set(sys.argv[1:])
    for src, dst in NAMES.items():
        if only and src not in only: continue
        pg.goto((HERE / f"{src}.html").as_uri()); pg.wait_for_timeout(300)
        big = OUT / f"{dst}.jpg"
        pg.screenshot(path=str(big), type="jpeg", quality=82)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(big), "-vf", "scale=640:360", "-q:v", "4",
                        str(OUT / f"{dst}-karta.jpg")], check=True)
        print(dst)
    b.close()
