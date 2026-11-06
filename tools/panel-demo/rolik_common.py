"""Общее для роликов демо-панели (#548, #552): польские подписи, нарисованный курсор, проверка кириллицы в кадре."""
import os, json
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "final.py")).read()
PL = eval(src.split("PL = ", 1)[1].split("\nJS = ")[0])
PL = [
 ["Техник дома: сервер, машины, сеть, копии, код, задания Клоду\\. ИИ на домашнем сервере, это не скрывает\\.", "Technik: serwer, maszyny wirtualne, sieć, kopie zapasowe, kod, zadania dla Claude. AI na własnym serwerze, nie ukrywa tego."],
 ["Собеседница и диктор дома: люди, дела, почта, кадры, деньги, новости\\. ИИ на домашнем сервере, это не скрывает\\.", "Rozmówczyni i lektorka: ludzie, sprawy, poczta, kadry, finanse, wiadomości. AI na własnym serwerze, nie ukrywa tego."],
 ["Модернизатор дома:[^]*", "Modernizator: sprawdza, co się zestarzało, co można ulepszyć i które nowe wersje są warte uwagi, potem decyduje, co wdrożyć. Pilnuje też planu nocnych kopii zapasowych. AI na własnym serwerze, nie ukrywa tego."],
 ["модернизатор, админ, аналитик, новостник, хранитель копий", "modernizacja, administracja, analiza, wiadomości, kopie"],
 ["кадры · бухгалтерия · диктор", "kadry · księgowość · lektor"], ["аналитика", "analiza"], ["новости", "wiadomości"], ["категория", "kategoria"],
] + PL
INIT_TPL = """(() => { const PL = __PL__;
 const tr = () => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
   while ((n = w.nextNode())) { let t = n.nodeValue, o = t; for (const [a, b] of PL) t = t.replace(new RegExp(a, 'g'), b); if (t !== o) n.nodeValue = t; }
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
CYR = """() => { const bad = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!/[\\u0400-\\u04FF]/.test(n.nodeValue)) continue; const e = n.parentElement; if (!e || !e.offsetParent) continue;
    if (getComputedStyle(e).visibility === 'hidden' || e.closest('[style*="visibility: hidden"]')) continue;
    const b = e.getBoundingClientRect(); if (b.bottom > 0 && b.top < innerHeight && b.width > 0 && b.right > 0 && b.left < innerWidth) bad.push(n.nodeValue.trim().slice(0, 60)); }
  return bad; }"""


def init(extra_pl=(), css=""):
    """Скрипт для add_init_script: свои замены идут первыми, css — доп. стили (скрыть лишнее)."""
    js = INIT_TPL.replace("__PL__", json.dumps(list(extra_pl) + PL, ensure_ascii=False))
    if css:
        js += "\naddEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = %s; document.head.appendChild(s); });" % json.dumps(css)
    return js
