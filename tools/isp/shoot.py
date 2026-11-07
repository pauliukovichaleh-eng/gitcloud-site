"""Zrzuty konsoli ISP z https://demo.gitcloud.pl (tylko ze stacji) w motywie „Kolor”, szare tła przemalowane na granat.
  python shoot.py dashboard=/,siec=/siec/wszystkie,ruch-asn=/siec/ruch-asn,ai-advisor=/ai-advisor,ai-router=/ai-router,proxmox-all=/proxmox <katalog>
Ukrywa przełącznik motywu, dzwonek, użytkownika i stopkę. „Historia alertów” nie brać (nazwisko klientki).
PNG → WebP (jakość 82) do public/img/demo/; punkty hotXY w src/components/Home.astro muszą trafiać w kadr."""
import sys, asyncio
from playwright.async_api import async_playwright
OUT=sys.argv[2].rstrip('/')+'/'   # katalog na PNG
PAGES=[x.split('=',1) for x in sys.argv[1].split(',')]   # name=path
HIDE=""".theme-toggle,.gc-notif-bell-wrap,.auth-user-chip,.auth-logout-link,.card-storm,.card-breath,.gc-notif-row[data-id="1"],.gc-notif-row-btn{display:none!important}
footer,.powered-by,[class*=powered]{display:none!important}"""
TINT="""(() => {
  const nav = (v, k) => { // szary → granat motywu Kolor
    const m = v.match(/rgba?\\(([\\d.]+), ([\\d.]+), ([\\d.]+)(?:, ([\\d.]+))?\\)/); if (!m) return null;
    const r=+m[1], g=+m[2], b=+m[3], a = m[4] === undefined ? 1 : +m[4];
    if (a === 0 || Math.abs(r-g) > 10 || Math.abs(g-b) > 10 || r > k) return null;
    const L = (r+g+b)/3, nr = Math.round(L*0.50), ng = Math.round(L*0.66), nb = Math.round(L*1.05 + 6);
    return `rgba(${nr}, ${ng}, ${nb}, ${a})`;
  };
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    const bg = nav(cs.backgroundColor, 70); if (bg) el.style.setProperty('background-color', bg, 'important');
    for (const s of ['Top','Right','Bottom','Left']) { const c = cs['border'+s+'Color'], w = parseFloat(cs['border'+s+'Width']);
      if (w > 0) { const n = nav(c, 110); if (n) el.style.setProperty('border-'+s.toLowerCase()+'-color', n.replace(/, [\\d.]+\\)$/, ', 1)').replace(/rgba\\((\\d+), (\\d+), (\\d+)/, (q,a,b,c)=>`rgba(${Math.min(255,+a+8)}, ${Math.min(255,+b+14)}, ${Math.min(255,+c+30)}`), 'important'); } }
  }
})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':1440,'height':900}, device_scale_factor=2, ignore_https_errors=True)
        pg = await ctx.new_page()
        for name, path in PAGES:
            try:
                await pg.goto('https://demo.gitcloud.pl'+path, wait_until='networkidle', timeout=60000)
                await pg.evaluate("document.documentElement.setAttribute('data-theme','color')")
                await pg.add_style_tag(content=HIDE)
                await pg.wait_for_timeout(2500)
                await pg.evaluate(TINT)
                await pg.wait_for_timeout(400)
                await pg.screenshot(path=OUT+name+'.png')
                print('ok', name, flush=True)
            except Exception as e: print('ERR', name, str(e)[:120], flush=True)
        await b.close()
asyncio.run(main())
