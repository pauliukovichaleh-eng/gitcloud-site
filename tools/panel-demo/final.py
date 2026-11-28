"""Zrzuty demo-panelu na stronę: polskie napisy, ukryte prywatne elementy, kadry, kontrola cyrylicy w kadrze (rolik_common.py)."""
import os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rolik_common import PL, TR, HIDE, CYR, DARK
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
# 18.11.2026: strona «Bezpieczeństwo» na fake_sec.py — ocena, tarcza wiadomości, dziennik złapanych
TARCZA = [("tarcza-panel", "/bezopasnost", 1440, 1000, 1000), ("tarcza-tel", "/bezopasnost", 390, 844, 844),
          ("tarcza-listy", "/bezopasnost", 1440, 1000, -1)]   # -1: kadr od nagłówka grupy «Tarcza wiadomości» do końca strony
mode = sys.argv[3] if len(sys.argv) > 3 else ""
if mode == "modele":   # круг 17: страница «Модели» на fake_llm.py
    SHOTS = MODELE
elif mode == "decyzje":
    SHOTS = DECYZJE
elif mode == "tarcza":
    SHOTS = TARCZA
elif mode == "faceid":   # 27.11.2026: karta strażnika (panel z DEMO_GUARD=1), jasny motyw, szczegóły rozwinięte
    SHOTS = [("decyzje-faceid", "/", 1440, 1000, 0), ("decyzje-faceid-tel", "/", 390, 844, 0)]
elif mode == "uczenia":   # 27.11.2026: Infra › Usługi › ćwiczenia „żywe awarie” (fake.py), jasny ton, sekcja rozwinięta
    SHOTS = [("infra-uczenia", "/infra", 1440, 1000, 0), ("infra-uczenia-tel", "/infra", 390, 844, 0)]
elif mode == "cwiczenia":   # 27.11.2026: Agenci › zakładka «Ćwiczenia» (fake.py: prawdziwy plan i dziennik), jasny ton, cała zakładka
    SHOTS = [("agenci-cwiczenia", "/agenty", 1440, 1000, 0), ("agenci-cwiczenia-tel", "/agenty", 390, 844, 0)]
LIGHT = ("faceid", "uczenia", "cwiczenia")
errs, cyr = [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--host-resolver-rules=MAP my.gitcloud.pl 127.0.0.1"])
    for name, path, w, h, ch in SHOTS:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 500 else int(os.environ.get("DSF", "1")), **({} if mode in LIGHT else DARK))
        ctx.add_cookies([{"name": "gc_lang", "value": "pl", "url": base}])
        # ton tylko w tej przeglądarce (28.11.2026: także ciemny — panel bierze ton ze wspólnego pliku hosta, a nie z motywu
        # systemu, więc same DARK dawały jasny kadr); zapis tonu na serwer (POST /tone) — odcięty, to wspólny plik hosta
        tone = "light" if mode in LIGHT else "dark"
        ctx.add_init_script(f"localStorage.setItem('gc-tone', JSON.stringify({{m: '{tone}', at: 9e12}}))")
        ctx.route("**/tone/**", lambda r: r.abort())
        pg = ctx.new_page()
        pg.on("console", lambda m, n=name: m.type == "error" and errs.append(f"{n}: {m.text[:120]}"))
        pg.on("response", lambda r, n=name: r.status >= 400 and errs.append(f"{n}: {r.status} {r.url}"))
        pg.goto(base + path, wait_until="domcontentloaded"); pg.wait_for_timeout(3000)
        pg.evaluate(TR, PL); pg.wait_for_timeout(300); pg.evaluate(TR, PL); pg.evaluate(HIDE)
        if mode == "tarcza":   # ochrona mieszkania to prywatna część domu, nie tarcza; zrzut bez niej
            pg.add_style_tag(content="[data-key=guard]{display:none!important}")
        hs = pg.evaluate("document.documentElement.scrollWidth > innerWidth")
        if mode == "cwiczenia":   # kadr: wszystkie bloki zakładki (na komputerze dwie kolumny, bez pustej pracowni demo)
            pg.add_style_tag(content=".ai-page[data-pane-on][data-pane-on][data-pane-on] > section[data-key=ws-none], #gc-tabbar{display:none!important}")
            pg.evaluate("document.querySelector('[data-pane-btn=e]').click()"); pg.wait_for_timeout(800)
            pg.locator('[data-key=uch-hud]').scroll_into_view_if_needed(); pg.wait_for_timeout(2500); pg.evaluate(TR, PL)
            bb = pg.evaluate("""() => { const r = [...document.querySelectorAll('[data-pane=e]')].filter(e => e.offsetParent).map(e => e.getBoundingClientRect());
              const x = Math.min(...r.map(a => a.left)), y = Math.min(...r.map(a => a.top));
              return {x, y: y + scrollY, width: Math.max(...r.map(a => a.right)) - x, height: Math.max(...r.map(a => a.bottom)) - y}; }""")
            cyr[name] = pg.evaluate(CYR, {"y": bb["y"] - pg.evaluate("scrollY"), "h": bb["height"], "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": max(bb["x"] - 12, 0), "y": bb["y"] - 12, "width": min(bb["width"] + 24, w), "height": bb["height"] + 24}, full_page=True)
        elif mode == "uczenia":
            pg.click('[data-pane-btn="c"]'); pg.wait_for_timeout(600)
            el = pg.locator('[data-mon="drill"]').first
            el.locator('[data-mon-fold]').first.click(); pg.wait_for_timeout(600); pg.evaluate(TR, PL)
            el.scroll_into_view_if_needed(); pg.wait_for_timeout(300); bb = el.bounding_box()
            cyr[name] = pg.evaluate(CYR, {"y": bb["y"], "h": bb["height"], "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": bb["x"] - 12, "y": bb["y"] - 12, "width": bb["width"] + 24, "height": bb["height"] + 24})
        elif mode == "faceid":
            el = pg.locator('[data-dq-id="900"]').first
            pg.evaluate("document.querySelector('[data-dq-id=\"900\"] .gc-dq-more').open = true"); pg.evaluate(TR, PL)
            el.scroll_into_view_if_needed(); pg.wait_for_timeout(300); bb = el.bounding_box()
            cyr[name] = pg.evaluate(CYR, {"y": bb["y"], "h": bb["height"], "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": bb["x"] - 12, "y": bb["y"] - 12, "width": bb["width"] + 24, "height": bb["height"] + 24})
        elif mode == "decyzje":
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
        elif ch < 0:
            top = pg.evaluate("""() => { const e = [...document.querySelectorAll('*')].find(x => x.children.length === 0 && /^Tarcza wiadomości$/i.test(x.textContent.trim()));
              return e ? e.getBoundingClientRect().top + scrollY - 24 : 0; }""")
            hh = pg.evaluate("document.documentElement.scrollHeight") - top
            pg.evaluate(f"scrollTo(0, {top})"); pg.wait_for_timeout(300)
            cyr[name] = pg.evaluate(CYR, {"y": top - pg.evaluate("scrollY"), "h": hh, "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": 0, "y": top, "width": w, "height": hh}, full_page=True)
        else:
            cyr[name] = pg.evaluate(CYR, {"y": 0, "h": ch, "w": w})
            pg.screenshot(path=f"{out}/{name}.png", clip={"x": 0, "y": 0, "width": w, "height": ch})
        print(name, "hscroll:", hs)
        ctx.close()
    b.close()
print("errors:", *errs, sep="\n  ")
print("cyrillic:", cyr)
