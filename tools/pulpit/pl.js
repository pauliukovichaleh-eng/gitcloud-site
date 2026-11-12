/* Polskie napisy aplikacji pulpitu na czas nagrania (tools/pulpit, README.md). Pulpit ma interfejs po rosyjsku; ten skrypt
   podmienia teksty węzłów i podpowiedzi (title, placeholder, aria-label, data-tip) według słownika SL, także w treści
   dopisywanej później (MutationObserver). Nieprzetłumaczony widoczny tekst z cyrylicą idzie do zbieracza
   (sesja.sh, port 18799) — z tej listy uzupełnia się słownik. */
(() => {
  const SL = __SL__;
  const RX = __RX__.map(([a, b]) => [new RegExp(a, 'g'), b]);
  const CYR = /[Ѐ-ӿ]/, ATTR = ['title', 'placeholder', 'aria-label', 'data-tip', 'data-title'];
  const seen = new Set();
  const tr = (s) => {
    if (!s || !CYR.test(s)) return s;
    const t = s.trim();
    if (SL[t] !== undefined) return s.replace(t, SL[t]);
    let o = s; for (const [a, b] of RX) o = o.replace(a, b);
    if (CYR.test(o) && !seen.has(t)) { seen.add(t); try { fetch('http://127.0.0.1:18799/miss', {method: 'POST', mode: 'no-cors', body: location.pathname + '\t' + t}); } catch (e) {} }
    return o;
  };
  const el = (e) => { for (const a of ATTR) { const v = e.getAttribute && e.getAttribute(a); if (v && CYR.test(v)) { const t = tr(v); if (t !== v) e.setAttribute(a, t); } } };
  const walk = (root) => {
    if (root.nodeType === 3) { const v = tr(root.nodeValue); if (v !== root.nodeValue) root.nodeValue = v; return; }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    if (root.nodeType === 1) { if (/^(SCRIPT|STYLE)$/.test(root.tagName)) return; el(root); }
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT); let n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) { if (n.parentElement && /^(SCRIPT|STYLE)$/.test(n.parentElement.tagName)) continue; const v = tr(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; } else el(n); }
  };
  const go = () => { walk(document.body || document.documentElement); if (document.title) document.title = tr(document.title);
    new MutationObserver((ms) => { for (const m of ms) { if (m.type === 'characterData') walk(m.target); else if (m.type === 'attributes') el(m.target); else m.addedNodes.forEach(walk); } })
      .observe(document.documentElement, {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTR}); };
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', go); else go();
})();
