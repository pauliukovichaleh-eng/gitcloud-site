"""Klatki głów agentów na stronę (public/img/agenci/*.webp, projekty/glowa-*.mp4). Przeniesione 07.11.2026 z
~/exports/agent-faces-2026-11-05/v2/clipgpu.py dla nocnego odświeżania (decyzja #748). Głowa: ~/src/gitcloud-remote/head
na http://127.0.0.1:8788 (python3 -m http.server). NAGRYWAĆ NA KARCIE GRAFICZNEJ (Vulkan, Radeon), nie SwiftShader;
Tony w head.js = „vale”; &nobrowcards=1 (brwi jak w eterze). Porównać klatkę z żywą stroną 127.0.0.1:8770.

Клипы эмоций голов для аватаров my.gitcloud.pl (24.10.2026, владелец: «не крутиться — уникальная эмоция каждого,
чтобы выглядели живыми»). head/ на http://127.0.0.1:8788 (python3 -m http.server), Chrome со SwiftShader, ?clip — head.js
отдаёт window.gcMood / gcEmo. Время подменено: requestAnimationFrame и performance.now идут шагами 1/FPS, поэтому
моргания и мимика в клипе — с настоящей скоростью, как бы медленно ни рисовал SwiftShader.
  head-clips.py <who> <папка> [секунд]   → <папка>/<who>_NNN.png; сценарий эмоций — SCRIPT ниже."""
import sys
from playwright.sync_api import sync_playwright

FPS = 15
SCRIPT = {   # (секунда, эмоция) — своя у каждого: Салли тёплая и игривая, Тони уверенный техник, Марк думающий аналитик
    "sally": [(0, "calm"), (1.2, "amused"), (3.6, "playful"), (5.4, "calm")],
    "vale": [(0, "confident"), (1.6, "interested"), (3.4, "thoughtful"), (5.2, "confident")],
    "mark": [(0, "thoughtful"), (1.8, "skeptical"), (3.6, "curious"), (5.4, "thoughtful")],
}
VCLOCK = """(() => {
  let vt = 0; const q = [];
  performance.now = () => vt; const D0 = Date.now(); Date.now = () => D0 + vt;
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {};
  window.__step = (ms) => { vt += ms; const run = q.splice(0); run.forEach((cb) => { try { cb(vt); } catch (e) {} }); };
})();"""

who, out = sys.argv[1], sys.argv[2]
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 6.6
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--headless=new", "--use-angle=vulkan", "--enable-features=Vulkan", "--ignore-gpu-blocklist", "--enable-gpu"])
    pg = b.new_page(device_scale_factor=3, viewport={"width": int(__import__("os").environ.get("SZ","480")), "height": int(__import__("os").environ.get("SZ","480"))})
    pg.set_default_timeout(180000)
    pg.add_init_script(VCLOCK)
    pg.goto(f"http://127.0.0.1:8788/index.html?who={who}&offline=1&clip=1&pr=3&nobrowcards=1&mood={SCRIPT[who][0][1]}", wait_until="load")
    for _ in range(600):                                  # загрузка модели: шагаем время, пока голова не готова
        pg.evaluate("window.__step(33)")
        if pg.evaluate("!!window.gcReady"):
            break
        pg.wait_for_timeout(30)
    for _ in range(60):
        pg.evaluate("window.__step(33)")                  # 2 с разгона: моргание, взгляд встают в обычный ход
    plan = list(SCRIPT[who])
    n = int(secs * FPS)
    for i in range(n):
        t = i / FPS
        while plan and plan[0][0] <= t:
            pg.evaluate(f"window.gcMood({plan.pop(0)[1]!r})")
        pg.evaluate(f"window.__step({1000 / FPS})")
        pg.screenshot(path=f"{out}/{who}_{i:03d}.png")
    print(who, n, "кадров")
    b.close()
