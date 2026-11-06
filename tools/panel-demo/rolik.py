"""Ролик «Agenci AI» (круг 39, #548): запись демо-панели (tools/panel-demo, выдуманные данные) через CDP screencast."""
import sys, os, json, base64, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
base, out = "http://my.gitcloud.pl:18932", sys.argv[1]
os.makedirs(out + "/frames", exist_ok=True)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "final.py")).read()
PL = eval(src.split("PL = ", 1)[1].split("\nJS = ")[0])
PL = [
 ["Техник дома: сервер, машины, сеть, копии, код, задания Клоду\\. ИИ на домашнем сервере, это не скрывает\\.", "Technik: serwer, maszyny wirtualne, sieć, kopie zapasowe, kod, zadania dla Claude. AI na własnym serwerze, nie ukrywa tego."],
 ["Собеседница и диктор дома: люди, дела, почта, кадры, деньги, новости\\. ИИ на домашнем сервере, это не скрывает\\.", "Rozmówczyni i lektorka: ludzie, sprawy, poczta, kadry, finanse, wiadomości. AI na własnym serwerze, nie ukrywa tego."],
 ["Модернизатор дома:[^]*", "Modernizator: sprawdza, co się zestarzało, co można ulepszyć i które nowe wersje są warte uwagi, potem decyduje, co wdrożyć. Pilnuje też planu nocnych kopii zapasowych. AI na własnym serwerze, nie ukrywa tego."],
 ["модернизатор, админ, аналитик, новостник, хранитель копий", "modernizacja, administracja, analiza, wiadomości, kopie"],
 ["кадры · бухгалтерия · диктор", "kadry · księgowość · lektor"], ["аналитика", "analiza"], ["новости", "wiadomości"], ["категория", "kategoria"],
] + PL
INIT = """(() => { const PL = __PL__;
 const tr = () => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
   while ((n = w.nextNode())) { let t = n.nodeValue, o = t; for (const [a, b] of PL) t = t.replace(new RegExp(a, 'g'), b); if (t !== o) n.nodeValue = t; }
   document.querySelectorAll('section.devices-panel').forEach(s => { if (/harmonogram/i.test(s.querySelector('*')?.textContent || s.textContent.slice(0, 80))) s.style.visibility = 'hidden'; });
   const m = [...document.querySelectorAll('details.gc-more')]; m.forEach(d => { let x = d; while (x) { x.style.display = 'none'; x = x.nextElementSibling; } }); };
 const cur = () => { if (document.getElementById('fcur')) return; const c = document.createElement('div'); c.id = 'fcur';
   c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,.18);border:2px solid #fff;box-shadow:0 0 12px #22d3ee;z-index:2147483647;pointer-events:none;transform:translate(-50%,-50%);transition:transform .12s';
   document.body.appendChild(c);
   addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
   addEventListener('mousedown', () => c.style.transform = 'translate(-50%,-50%) scale(.7)', true);
   addEventListener('mouseup', () => c.style.transform = 'translate(-50%,-50%)', true);
   const p = sessionStorage.getItem('fcur'); if (p) { const [x, y] = JSON.parse(p); c.style.left = x + 'px'; c.style.top = y + 'px'; }
   addEventListener('mousemove', e => sessionStorage.setItem('fcur', JSON.stringify([e.clientX, e.clientY])), true); };
 addEventListener('DOMContentLoaded', () => { tr(); cur(); new MutationObserver(() => { clearTimeout(window.__t); window.__t = setTimeout(tr, 0); }).observe(document.body, {subtree: true, childList: true, characterData: true}); });
})();""".replace("__PL__", json.dumps(PL, ensure_ascii=False))
CYR = """() => { const bad = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!/[\\u0400-\\u04FF]/.test(n.nodeValue)) continue; const e = n.parentElement; if (!e || !e.offsetParent) continue;
    if (getComputedStyle(e).visibility === 'hidden' || e.closest('[style*="visibility: hidden"]')) continue;
    const b = e.getBoundingClientRect(); if (b.bottom > 0 && b.top < innerHeight && b.width > 0 && b.right > 0 && b.left < innerWidth) bad.push(n.nodeValue.trim().slice(0, 60)); }
  return bad; }"""
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
