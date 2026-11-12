"""Wspólne dla zrzutów (final.py) i filmów (rolik.py, rolik_panel.py) demo-panelu: polskie napisy, ukrywanie
prywatnych elementów, narysowany kursor, kontrola cyrylicy w kadrze."""
import json

# Zamiany napisów (regex → tekst), kolejno; najpierw dłuższe. Role agentów jak na stronie: Sally korespondencja i terminy,
# Tony dyżur infrastruktury, Mark modernizacja i analiza.
PL = [
    ["Техник дома: сервер, машины, сеть, копии, код, задания Клоду\\. ИИ на домашнем сервере, это не скрывает\\.",
     "Dyżurny infrastruktury: serwer, maszyny wirtualne, sieć, kopie zapasowe, alarmy. AI na własnym serwerze, nie ukrywa tego."],
    ["Собеседница и диктор дома:[^]*", "Korespondencja i terminy: poczta, sprawy, przypomnienia. AI na własnym serwerze, nie ukrywa tego."],
    ["Модернизатор дома:[^]*", "Modernizacja i analiza: sprawdza, co się zestarzało i które nowe wersje są warte uwagi, potem proponuje wdrożenie. AI na własnym serwerze, nie ukrywa tego."],
    ["модернизатор, админ, аналитик, новостник, хранитель копий", "modernizacja, administracja, analiza, kopie"],
    [r"из (\d+) действий", "z $1 działań"], ["[hH][rR], бухгалтер и диктор", "korespondencja i terminy"],
    ["kadry · księgowość · lektor", "korespondencja i terminy"], ["кадры · бухгалтерия · диктор", "korespondencja i terminy"],
    ["kadry, księgowość i lektor", "korespondencja i terminy"], ["Вживую", "Na żywo"], ["Мастерская", "Warsztat"],
    ["меньше: ", "najmniej: "], ["ответов", "odpowiedzi"], ["сломано", "zepsute"], ["отказов", "odmów"], ["провал экзамена", "egzamin oblany"],
    ["категория", "kategoria"], ["аналитика", "analiza"], ["новости", "wiadomości"], ["Открыть", "Otwórz"], ["дольше всех", "najdłużej"],
    [" мин", " min"], ["(\\d) ч(?![а-я])", "$1 godz."], ["само: ", "automatycznie: "], ["Claude готовит", "Claude przygotowuje"], ["вопросы", "pytania"],
    ["Решила", "Zdecydowała"], ["Отправила", "Wysłała"], ["Решил", "Zdecydował"], ["Отправил", "Wysłał"],
    ["пн (\\d)", "pn $1"], ["вт (\\d)", "wt $1"], ["ср (\\d)", "śr $1"], ["чт (\\d)", "czw $1"], ["пт (\\d)", "pt $1"], ["сб (\\d)", "sob $1"], ["вс (\\d)", "nd $1"],
]
# Funkcje JS (tekst do page.evaluate albo do skryptu startowego).
TR = """(pl) => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { let t = n.nodeValue, o = t; for (const [a, b] of pl) t = t.replace(new RegExp(a, 'g'), b); if (t !== o) n.nodeValue = t; } }"""
HIDE_SEL = "[data-key='hud-now'], [data-key='hud-cena'], .auth-user-chip"   # pasek finansów, «Dom (tylko odczyt)»
# 10.11.2026: w kadrze bez „Dom (tylko odczyt)” w nagłówku, bez przycisku mostu „Dom ↔ Praca” i bez paska finansów (prywatne)
HIDE = """() => { for (const e of document.querySelectorAll('body *')) { const t = (e.textContent || '').replace(/\\s+/g, ' ').trim();
  if (/^Dom \\(tylko odczyt\\)$/.test(t) || /^Дом ↔ Работа$/.test(t) || /^Dom ↔ Praca$/.test(t)) e.style.visibility = 'hidden'; }
  for (const e of document.querySelectorAll(HIDE_SEL)) e.style.display = 'none'; }""".replace("HIDE_SEL", json.dumps(HIDE_SEL))
# cyrylica w widocznym prostokącie r = {y, h, w} (bez r — cały ekran)
CYR = """(r) => { r = r || {y: 0, h: innerHeight, w: innerWidth}; const bad = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!/[\\u0400-\\u04FF]/.test(n.nodeValue)) continue; const e = n.parentElement; if (!e || !e.offsetParent) continue;
    if (getComputedStyle(e).visibility === 'hidden' || e.closest('[style*="visibility: hidden"]')) continue;
    const b = e.getBoundingClientRect(); if (b.bottom > r.y && b.top < r.y + r.h && b.width > 0 && b.right > 0 && b.left < r.w) bad.push(n.nodeValue.trim().slice(0, 60)); }
  return bad; }"""
INIT_TPL = """(() => { const PL = __PL__; const TR = __TR__; const HIDE = __HIDE__;
 const st = document.createElement('style'); st.textContent = __SEL__ + ' { display: none !important; }'; const put = () => { if (!document.documentElement) return false; document.documentElement.appendChild(st); return true; };
 if (!put()) { const o = new MutationObserver(() => { if (put()) o.disconnect(); }); o.observe(document, {childList: true}); }
 const tr = () => { TR(PL); HIDE();
   if (location.pathname.startsWith('/agenty')) document.querySelectorAll('section.devices-panel').forEach(s => { if (/harmonogram/i.test(s.querySelector('*')?.textContent || s.textContent.slice(0, 80))) s.style.visibility = 'hidden'; });
   const m = location.pathname.startsWith('/agenty') ? [...document.querySelectorAll('details.gc-more')] : []; m.forEach(d => { let x = d; while (x) { x.style.display = 'none'; x = x.nextElementSibling; } }); };
 const cur = () => { if (document.getElementById('fcur')) return; const c = document.createElement('div'); c.id = 'fcur';
   c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,.18);border:2px solid #fff;box-shadow:0 0 12px #22d3ee;z-index:2147483647;pointer-events:none;transform:translate(-50%,-50%);transition:transform .12s';
   document.body.appendChild(c);
   addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
   addEventListener('mousedown', () => c.style.transform = 'translate(-50%,-50%) scale(.7)', true);
   addEventListener('mouseup', () => c.style.transform = 'translate(-50%,-50%)', true);
   const p = sessionStorage.getItem('fcur'); if (p) { const [x, y] = JSON.parse(p); c.style.left = x + 'px'; c.style.top = y + 'px'; }
   addEventListener('mousemove', e => sessionStorage.setItem('fcur', JSON.stringify([e.clientX, e.clientY])), true); };
 addEventListener('DOMContentLoaded', () => { tr(); cur(); new MutationObserver(() => { clearTimeout(window.__t); window.__t = setTimeout(tr, 0); }).observe(document.body, {subtree: true, childList: true, characterData: true}); });
})();"""


def init(extra_pl=(), css=""):
    """Skrypt dla add_init_script filmów: własne zamiany idą pierwsze, css — dodatkowe style (ukryć zbędne)."""
    js = (INIT_TPL.replace("__PL__", json.dumps(list(extra_pl) + PL, ensure_ascii=False))
          .replace("__TR__", TR).replace("__HIDE__", HIDE).replace("__SEL__", json.dumps(HIDE_SEL)))
    if css:
        js += "\naddEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = %s; document.head.appendChild(s); });" % json.dumps(css)
    return js


def koduj(out, name):
    """Klatki screencastu (meta.json: [czas, plik]) → public/img/projekty/<name>.mp4 i plakat <plakat>.jpg (klatka 2. sekundy)."""
    import subprocess
    from pathlib import Path
    proj = Path(__file__).resolve().parents[2] / "public/img/projekty"
    fr = json.load(open(f"{out}/meta.json"))["frames"]
    lines = ["ffconcat version 1.0"]
    for (t, f), (t2, _) in zip(fr, fr[1:] + [[fr[-1][0] + 1.0, None]]):
        lines += [f"file '{f}'", f"duration {max(t2 - t, 0.001):.4f}"]
    lines.append(f"file '{fr[-1][1]}'")
    open(f"{out}/list.ffconcat", "w").write("\n".join(lines) + "\n")
    mp4 = proj / f"{name}.mp4"
    subprocess.run(["nice", "-n", "19", "ffmpeg", "-y", "-loglevel", "error", "-threads", "2", "-f", "concat", "-safe", "0",
                    "-i", f"{out}/list.ffconcat", "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "veryslow",
                    "-crf", "28", "-tune", "stillimage", "-movflags", "+faststart", "-an", str(mp4)], check=True)
    poster = min(fr, key=lambda x: abs(x[0] - 2.0))[1]
    jpg = proj / {"agenci": "agenci-wideo.jpg", "panel": "panel-wideo.jpg"}[name]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", poster, "-q:v", "3", str(jpg)], check=True)
    print(mp4.name, mp4.stat().st_size // 1024, "KB;", jpg.name, jpg.stat().st_size // 1024, "KB")
