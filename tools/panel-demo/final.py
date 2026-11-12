"""Zrzuty demo-panelu na stronę: polskie napisy, ukryte prywatne elementy, kadry, kontrola cyrylicy w kadrze (rolik_common.py)."""
import os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rolik_common import PL, TR, HIDE, CYR
base, out = sys.argv[1], sys.argv[2]   # [modele]
SHOTS = [  # (имя, путь, ширина, высота, высота кадра)
    ("panel-agenci", "/agenty", 1440, 900, 790),
    ("panel-tony", "/agenty/tony", 1440, 900, 625),
    ("panel-sally", "/agenty/sally", 1440, 900, 640),
    ("panel-agenci-tel", "/agenty", 390, 844, 844),
]
MODELE = [("panel-modele", "/ai-router", 1440, 1000, 985), ("panel-modele-tel", "/ai-router", 390, 844, 844)]
# круг 19: пульт Claude на Главной — карточки «Решения» (fake_dec.py); кадр = сам виджет, ("sel", раскрыть, ширина)
DECYZJE = [("panel-decyzje", "/", 1440, 1000, 0), ("panel-decyzje-szczegoly", "/", 1440, 1000, 0), ("panel-decyzje-tel", "/", 390, 844, 0)]
mode = sys.argv[3] if len(sys.argv) > 3 else ""
if mode == "modele":   # круг 17: страница «Модели» на fake_llm.py
    SHOTS = MODELE
elif mode == "decyzje":
    SHOTS = DECYZJE
errs, cyr = [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--host-resolver-rules=MAP my.gitcloud.pl 127.0.0.1"])
    for name, path, w, h, ch in SHOTS:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 500 else int(os.environ.get("DSF", "1")))
        ctx.add_cookies([{"name": "gc_lang", "value": "pl", "url": base}])
        pg = ctx.new_page()
        pg.on("console", lambda m, n=name: m.type == "error" and errs.append(f"{n}: {m.text[:120]}"))
        pg.on("response", lambda r, n=name: r.status >= 400 and errs.append(f"{n}: {r.status} {r.url}"))
        pg.goto(base + path, wait_until="domcontentloaded"); pg.wait_for_timeout(3000)
        pg.evaluate(TR, PL); pg.wait_for_timeout(300); pg.evaluate(TR, PL); pg.evaluate(HIDE)
        hs = pg.evaluate("document.documentElement.scrollWidth > innerWidth")
        if mode == "decyzje":
            pg.add_style_tag(content="#gc-tabbar{display:none!important}")
            el = pg.locator('[data-key="decide"]').first
            if name.endswith("szczegoly"):   # подробности первой карточки и журнал решений раскрыты
                pg.evaluate("""() => { document.querySelector('[data-key=decide] .gc-dq-more').open = true;
                                       document.querySelector('[data-key=clx-journal]').open = true; }""")
                s1 = pg.locator('[data-key="cc:s1"]')   # 11.11.2026: rozwinięta sesja w toku — nić sprawy (fake_dec.PLANS)
                if s1.count():
                    s1.first.click(); pg.wait_for_timeout(1200)
                pg.evaluate(TR, PL); pg.wait_for_timeout(400)
            el.scroll_into_view_if_needed(); bb = el.bounding_box()
            sy = pg.evaluate("scrollY"); top = bb["y"] + sy
            if w < 500:   # телефон: только шапка и карточки, до полос лимитов
                lim = pg.evaluate("""() => { const e = [...document.querySelectorAll('[data-key=decide] *')].find(x => /^SESJA|^Sesja/i.test(x.textContent.trim()) && x.children.length < 3);
                  return e ? e.getBoundingClientRect().top + scrollY : 0; }""")
                bb["height"] = (lim - top - 12) if lim > top else min(bb["height"], 1150)
            cyr[name] = pg.evaluate(CYR, {"y": bb["y"], "h": bb["height"], "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": bb["x"] - 6, "y": top - 6, "width": bb["width"] + 12, "height": bb["height"] + 12}, full_page=True)
        else:
            cyr[name] = pg.evaluate(CYR, {"y": 0, "h": ch, "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": 0, "y": 0, "width": w, "height": ch})
        print(name, "hscroll:", hs)
        ctx.close()
    b.close()
print("errors:", *errs, sep="\n  ")
print("cyrillic:", cyr)
