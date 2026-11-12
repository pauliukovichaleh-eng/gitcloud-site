"""Ролик «Panel operacyjny» (круг 40, #552): запись демо-панели (выдуманные данные) через CDP screencast.
Сценарий: пульт Claude на Главной → подробности вопроса Марка → ответ одним нажатием (5 с на отмену, потом
«w realizacji», карточка уходит в журнал) → журнал решений с итогом → вкладка «Modele» (сальдо, вызовы, оценки моделей).
Перед записью демо-панель запускать заново: ответ меняет данные fake_dec.py до перезапуска."""
import sys, os, json, base64
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rolik_common import init, CYR, koduj
base, out = "http://my.gitcloud.pl:18932", sys.argv[1]
os.makedirs(out + "/frames", exist_ok=True)
# подписи из app.js ядра (тост gcAct, карточка решения) — по-польски, без длинного тире
EXTRA = [["^Ответ: ", "Odpowiedź: "], ["Отменить", "Cofnij"], [" — исполняется", " · w realizacji"], ["исполняется…", "w realizacji…"],
         ["изменить:", "zmień:"], ["журнал решений", "dziennik decyzji"]]
frames, errs, cyr = [], [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--host-resolver-rules=MAP my.gitcloud.pl 127.0.0.1"])
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    ctx.add_cookies([{"name": "gc_lang", "value": "pl", "url": base}])
    ctx.add_init_script(init(EXTRA))   # pasek finansów, «Dom (tylko odczyt)», most — ukrywa HIDE
    pg = ctx.new_page()
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text[:120]))
    pg.on("response", lambda r: r.status >= 400 and errs.append(f"{r.status} {r.url}"))
    for u in ("/agenty", "/ai-router", "/"):   # прогрев кэша
        pg.goto(base + u, wait_until="networkidle")
    pg.wait_for_timeout(500)
    cdp = ctx.new_cdp_session(pg)
    t0 = [None]

    def on_frame(ev):
        cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        ts = ev["metadata"]["timestamp"]
        if t0[0] is None:
            t0[0] = ts
        fn = f"{out}/frames/{len(frames):05d}.jpg"
        open(fn, "wb").write(base64.b64decode(ev["data"]))
        frames.append((ts - t0[0], fn))
    cdp.on("Page.screencastFrame", on_frame)

    def mv(x, y, steps=18): pg.mouse.move(x, y, steps=steps)
    def scroll(y, ms=800): pg.evaluate(f"window.scrollTo({{top:{y},behavior:'smooth'}})"); pg.wait_for_timeout(ms)
    def check(tag): cyr[tag] = pg.evaluate(CYR)
    def to(sel, steps=22):
        el = pg.locator(sel).first; bb = el.bounding_box()
        mv(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2, steps); pg.wait_for_timeout(150); return el
    def go(sel, wait=1200, nav=False):
        el = to(sel); el.click()
        if nav: pg.wait_for_load_state("networkidle")
        pg.wait_for_timeout(wait)

    pg.goto(base + "/", wait_until="networkidle"); pg.mouse.move(1300, 200); pg.wait_for_timeout(400)
    cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": 1280, "maxHeight": 720, "everyNthFrame": 1})
    pg.wait_for_timeout(2200); check("home-top")
    q1 = "[data-key=decide] [data-dq-id='900']"
    go(f"{q1} .gc-dq-more summary", 1900); check("home-more")
    go(f"{q1} .gc-dq-btn[data-k='1']", 1400); check("home-toast")
    mv(820, 420, 30); pg.wait_for_timeout(4600); check("home-done")      # 5 с отмены, потом POST и обновление
    pg.wait_for_timeout(1200)
    jy = pg.evaluate("document.querySelector('[data-key=clx-journal]').getBoundingClientRect().top + scrollY")
    scroll(max(0, jy - 330), 1000)
    go("[data-key=clx-journal] > summary", 2600); check("home-journal")
    go("a[href='/agenty']", 900, nav=True)
    go("a[href='/ai-router']", 2400, nav=True); check("modele-top")
    to("text=WYWOŁANIA WG DNI", 30); pg.wait_for_timeout(600)
    scroll(330, 1200); pg.wait_for_timeout(600); check("modele-330")
    go("text=qwen3:4b-instruct", 2600); check("modele-row")
    cdp.send("Page.stopScreencast"); pg.wait_for_timeout(200)
    b.close()
json.dump({"frames": frames, "errs": errs, "cyr": cyr}, open(out + "/meta.json", "w"), ensure_ascii=False, indent=0)
print("frames", len(frames), "dur", round(frames[-1][0], 2)); print("errs", errs); print("cyr", cyr)
koduj(out, "panel")
