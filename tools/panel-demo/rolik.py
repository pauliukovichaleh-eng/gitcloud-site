"""Ролик «Agenci AI» (круг 39, #548): запись демо-панели (tools/panel-demo, выдуманные данные) через CDP screencast."""
import sys, os, json, base64, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
base, out = "http://my.gitcloud.pl:18932", sys.argv[1]
os.makedirs(out + "/frames", exist_ok=True)
from rolik_common import init, CYR, koduj
INIT = init()
frames, errs, cyr = [], [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--host-resolver-rules=MAP my.gitcloud.pl 127.0.0.1"])
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    ctx.add_cookies([{"name": "gc_lang", "value": "pl", "url": base}])
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text[:120]))
    pg.on("response", lambda r: r.status >= 400 and errs.append(f"{r.status} {r.url}"))
    # прогрев: кэш картинок/шрифтов, чтобы в записи не было пустых кадров
    for u in ("/agenty/tony", "/agenty/sally", "/agenty/mark", "/agenty"):
        pg.goto(base + u, wait_until="networkidle")
    pg.wait_for_timeout(500)
    cdp = ctx.new_cdp_session(pg)
    t0 = [None]
    def on_frame(ev):
        cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        ts = ev["metadata"]["timestamp"]
        if t0[0] is None: t0[0] = ts
        fn = f"{out}/frames/{len(frames):05d}.jpg"
        open(fn, "wb").write(base64.b64decode(ev["data"])); frames.append((ts - t0[0], fn))
    cdp.on("Page.screencastFrame", on_frame)
    def start(): cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": 1280, "maxHeight": 720, "everyNthFrame": 1})
    def mv(x, y, steps=18): pg.mouse.move(x, y, steps=steps)
    def scroll(y, ms=700):
        pg.evaluate(f"window.scrollTo({{top:{y},behavior:'smooth'}})"); pg.wait_for_timeout(ms)
    def check(tag): cyr[tag] = pg.evaluate(CYR)
    def go(sel_or_xy, wait=1200):
        el = pg.locator(sel_or_xy).first; bb = el.bounding_box()
        mv(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2, 22); pg.wait_for_timeout(150)
        el.click(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(wait)
    pg.goto(base + "/agenty", wait_until="networkidle"); pg.mouse.move(640, 300); pg.wait_for_timeout(300)
    pg.evaluate("scrollTo(0,0)")
    start(); pg.wait_for_timeout(2600); check("agenty-top")
    scroll(205, 900); check("agenty-205")
    go("button:has-text('Tydzień')", 1100)
    go("summary:has-text('Restart usługi app-web')", 1800); check("agenty-row")
    go("a[href='/agenty/tony']:has-text('Tony') >> nth=1", 2200); check("tony-top")
    scroll(330, 1100); pg.wait_for_timeout(1700); check("tony-330")
    scroll(0, 700)
    go(".card a[href='/agenty/sally']", 2600); check("sally-top")
    go(".card a[href='/agenty/mark']", 2600); check("mark-top")
    cdp.send("Page.stopScreencast"); pg.wait_for_timeout(200)
    b.close()
json.dump({"frames": frames, "errs": errs, "cyr": cyr}, open(out + "/meta.json", "w"), ensure_ascii=False, indent=0)
print("frames", len(frames), "dur", round(frames[-1][0], 2)); print("errs", errs); print("cyr", cyr)
koduj(out, "agenci")
