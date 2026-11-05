#!/usr/bin/env python3
"""Buduje katalog projektów gitcloud.pl z projects/projects.json.

  python3 tools/build_projects.py          -> index.html (strona główna), projekty/index.html, projekty/<slug>/index.html, sitemap.xml
  python3 tools/build_projects.py --check  -> tylko sprawdzenie danych (kod 1 przy błędzie)

Zasady (strona publiczna): bez nazw pracodawcy i klientów, bez długich myślników, bez prywatnych adresów IP.
Lista FORBIDDEN poniżej; build się zatrzymuje, jeśli coś z niej trafi do danych albo do wygenerowanego HTML.
Tylko biblioteka standardowa.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "projects" / "projects.json"
OUT = ROOT / "projekty"
SITE = "https://gitcloud.pl"

# Nazwy, których nie wolno publikować bez zgody właściciela (pracodawca, klienci, lokalizacje).
OG_DEFAULT = "/img/og.jpg"  # tools/og/og.html → zrzut 1200x630

FORBIDDEN = [
    "staleks", "laito", "bestomed", "bestovet", "lukoszek", "mikrosilika", "wianecka", "kuriata",
    "łomianki", "lomianki", "hornówek", "hornowek",
]
DASHES = ["—", "–"]
PRIVATE_IP = re.compile(r"\b(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b")
CAT_RGB = {"wlasne": "90,164,255", "platformy": "62,207,142", "zlecenia": "224,179,77"}
REQUIRED = ["slug", "category", "title", "lead", "problem", "solution", "stack", "role", "results"]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
         '&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">')


def problems_in(text: str, where: str) -> list[str]:
    out = []
    low = text.lower()
    for w in FORBIDDEN:
        if w in low:
            out.append(f"{where}: zakazane słowo «{w}»")
    for d in DASHES:
        if d in text:
            out.append(f"{where}: długi myślnik U+{ord(d):04X}")
    m = PRIVATE_IP.search(text)
    if m:
        out.append(f"{where}: prywatny adres IP {m.group(0)}")
    return out


def validate(data: dict) -> list[str]:
    errs = []
    cats = data.get("categories", {})
    seen = set()
    for i, p in enumerate(data.get("projects", [])):
        tag = p.get("slug", f"#{i}")
        for k in REQUIRED:
            if not p.get(k):
                errs.append(f"{tag}: brak pola {k}")
        if not re.fullmatch(r"[a-z0-9-]+", p.get("slug", "")):
            errs.append(f"{tag}: slug tylko a-z0-9-")
        if tag in seen:
            errs.append(f"{tag}: powtórzony slug")
        seen.add(tag)
        if p.get("category") not in cats:
            errs.append(f"{tag}: nieznana kategoria {p.get('category')}")
        for src in [p.get("image"), p.get("thumb")] + [g.get(k) for g in p.get("gallery", []) for k in ("src", "video")] + \
                   [p.get("video", {}).get("src"), p.get("video", {}).get("poster")]:
            if src and src.startswith("/") and not (ROOT / src.lstrip("/")).is_file():
                errs.append(f"{tag}: brak pliku {src}")
    for f in data.get("featured", []):
        if f not in seen:
            errs.append(f"featured: nie ma projektu {f}")
    errs += problems_in(json.dumps(data, ensure_ascii=False), "projects.json")
    return errs


NAV = [("/", "Pracownia"), ("/projekty/", "Projekty"), ("/uslugi/", "Usługi"), ("/isp/", '<span class="lg">Platforma </span>ISP')]


def nav(active: str) -> str:
    return "\n".join(f'      <a href="{h}"{" class=\"active\"" if h == active else ""}>{n}</a>' for h, n in NAV)


def head(title: str, desc: str, path: str, extra: str = "", image: str = "", active: str = "/projekty/") -> str:
    url = SITE + path
    if not image or image.endswith(".png"):      # brak zdjęcia albo mały zrzut piksela: wspólna karta 1200x630
        image = OG_DEFAULT
    og_img = f'<meta property="og:image" content="{SITE}{escape(image)}">\n'
    if image == OG_DEFAULT:
        og_img += ('<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                   '<meta name="twitter:card" content="summary_large_image">\n')
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta name="author" content="Aleh Pauliukovich">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
{og_img}<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="GitCloud">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="/favicon-192.png">
{FONTS}
<link rel="stylesheet" href="/assets/projekty.css">
{extra}</head>
<body>
<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="/"><span class="git">Git</span><span class="cloud">Cloud</span><span class="dim">.pl</span></a>
    <nav class="tabs">
{nav(active)}
    </nav>
  </div>
</header>
<main>
"""


FOOT = """</main>
<footer><div class="wrap footer-row">
  <div>© 2026 GitCloud. Aleh Pauliukovich.</div>
  <a class="footer-link" href="/privacy.html">Polityka prywatności</a>
</div></footer>
"""


def jsonld(obj: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


def thumb(p: dict, eager: bool = False) -> str:
    img = p.get("thumb") or p.get("image")      # thumb: lżejsza wersja 640 px do kart
    if img:
        cls = ' class="px"' if p.get("pixelated") else ""
        load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'   # pierwsza karta = LCP katalogu
        return (f'<div class="thumb"><img src="{escape(img)}" alt="{escape(p.get("image_alt", p["title"]))}"'
                f'{cls} {load} width="640" height="360"></div>')
    rgb = CAT_RGB.get(p["category"], "90,164,255")
    big = escape(p["stack"][0])
    sub = escape(" · ".join(p["stack"][1:4]))
    return f'<div class="thumb gen" style="--rgb:{rgb}" aria-hidden="true"><div class="big">{big}</div><div class="sub">{sub}</div></div>'


def card(p: dict, cats: dict, h: str = "h2", eager: bool = False) -> str:
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in p["stack"][:5])
    return f"""  <a class="card" href="/projekty/{p['slug']}/" data-cat="{p['category']}">
    {thumb(p, eager)}
    <div class="body">
      <span class="cat cat-{p['category']}">{escape(cats[p['category']])} · {escape(p.get('year', ''))}</span>
      <{h}>{escape(p['title'])}</{h}>
      <p>{escape(p['lead'])}</p>
      <div class="tags">{tags}</div>
    </div>
  </a>"""


def build_index(data: dict) -> str:
    cats = data["categories"]
    projects = data["projects"]
    counts = {c: sum(1 for p in projects if p["category"] == c) for c in cats}
    btns = [f'<button type="button" data-f="*" aria-pressed="true">Wszystkie<span class="n">{len(projects)}</span></button>']
    btns += [f'<button type="button" data-f="{c}" aria-pressed="false">{escape(n)}<span class="n">{counts[c]}</span></button>'
             for c, n in cats.items() if counts[c]]
    cards = [card(p, cats, eager=(i == 0)) for i, p in enumerate(projects)]
    ld = jsonld({
        "@context": "https://schema.org", "@type": "CollectionPage", "name": "Projekty GitCloud",
        "url": f"{SITE}/projekty/", "inLanguage": "pl",
        "author": {"@type": "Person", "name": "Aleh Pauliukovich"},
        "hasPart": [{"@type": "CreativeWork", "name": p["title"], "url": f"{SITE}/projekty/{p['slug']}/"} for p in projects],
    })
    title = "Projekty: systemy AI, platformy i zlecenia | GitCloud"
    desc = "Katalog projektów pracowni GitCloud: agenci AI, firmware, platforma dla operatorów sieci, zlecenia dla sklepów internetowych. Zadanie, rozwiązanie, stack i wynik."
    return head(title, desc, "/projekty/", ld) + f"""<section class="hero">
  <div class="wrap">
    <div class="kicker">Pracownia AI · projekty</div>
    <h1>Co zbudowałem i dla kogo pracowałem</h1>
    <p class="lead">Systemy własne, platformy i zlecenia dla klientów. Przy każdym projekcie: zadanie, rozwiązanie, stack, moja rola i wynik w liczbach. Nazwy klientów pokazuję tylko za ich zgodą.</p>
    <div class="filters" role="group" aria-label="Filtr kategorii">
      {''.join(btns)}
    </div>
  </div>
</section>
<div class="wrap">
<div class="grid" id="grid">
{chr(10).join(cards)}
</div>
</div>
<script>
(function(){{var b=document.querySelectorAll('.filters button'),c=document.querySelectorAll('#grid .card');
b.forEach(function(x){{x.addEventListener('click',function(){{var f=x.dataset.f;
b.forEach(function(y){{y.setAttribute('aria-pressed',y===x?'true':'false')}});
c.forEach(function(k){{k.hidden=!(f==='*'||k.dataset.cat===f)}});}})}});
var h=location.hash.slice(1);if(h){{var t=document.querySelector('.filters button[data-f="'+h+'"]');if(t)t.click();}}}})();
</script>
""" + FOOT + "</body>\n</html>\n"


def build_page(data: dict, i: int) -> str:
    cats = data["categories"]
    projects = data["projects"]
    p = projects[i]
    path = f"/projekty/{p['slug']}/"
    media = ""
    if p.get("video"):
        v = p["video"]
        media = (f'<figure class="media"><video src="{escape(v["src"])}" poster="{escape(v.get("poster", ""))}" '
                 f'muted loop playsinline autoplay preload="metadata" width="640" height="316"></video></figure>')
    elif p.get("image"):
        cls = ' class="px"' if p.get("pixelated") else ""
        media = (f'<figure class="media"><img src="{escape(p["image"])}" alt="{escape(p.get("image_alt", p["title"]))}"'
                 f'{cls} width="960" height="474"></figure>')
    gallery = ""
    extra_imgs = [g for g in p.get("gallery", []) if g["src"] != p.get("image") or p.get("video")]
    if extra_imgs:
        def fig(g):
            if g.get("video"):
                el = (f'<video src="{escape(g["video"])}" poster="{escape(g["src"])}" muted loop playsinline controls '
                      f'preload="none" width="480" height="237" aria-label="{escape(g["alt"])}"></video>')
            else:
                el = (f'<img src="{escape(g["src"])}" alt="{escape(g["alt"])}"{" class=px" if g.get("pixelated") else ""} '
                      f'loading="lazy" width="480" height="270">')
            return f'<figure>{el}<figcaption>{escape(g["alt"])}</figcaption></figure>'
        figs = "".join(fig(g) for g in extra_imgs)
        note = f'<p class="gnote">{escape(p["gallery_note"])}</p>' if p.get("gallery_note") else ""
        gallery = f'<div class="wrap"><div class="gallery">{figs}</div>{note}</div>'
    elif p.get("gallery_note"):
        gallery = f'<div class="wrap"><p class="gnote" style="margin-top:12px">{escape(p["gallery_note"])}</p></div>'
    results = "".join(f"<li>{escape(r)}</li>" for r in p["results"])
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in p["stack"])
    links = ""
    if p.get("links"):
        links = '<div class="box links"><h3>Linki</h3>' + "<br>".join(
            f'<a href="{escape(l["href"])}">{escape(l["label"])}</a>' for l in p["links"]) + "</div>"
    prev_p, next_p = projects[i - 1], projects[(i + 1) % len(projects)]
    ld = jsonld({
        "@context": "https://schema.org", "@type": "CreativeWork", "name": p["title"], "description": p["lead"],
        "url": SITE + path, "inLanguage": "pl", "dateCreated": p.get("year"),
        "keywords": ", ".join(p["stack"]), "author": {"@type": "Person", "name": "Aleh Pauliukovich", "url": SITE + "/"},
        **({"image": SITE + p["image"]} if p.get("image") else {}),
    }) + jsonld({
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "GitCloud", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Projekty", "item": SITE + "/projekty/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": SITE + path}],
    })
    return head(f"{p['title']} | Projekty GitCloud", p["lead"], path, ld, p.get("image", "")) + f"""<section class="hero">
  <div class="wrap">
    <div class="crumbs"><a href="/projekty/">Projekty</a> / <span class="cat cat-{p['category']}">{escape(cats[p['category']])}</span></div>
    <h1>{escape(p['title'])}</h1>
    <p class="lead">{escape(p['lead'])}</p>
    <div class="meta-row"><span>Rok: <b>{escape(p.get('year', ''))}</b></span><span>Status: <b>{escape(p.get('status', ''))}</b></span></div>
    {media}
  </div>
</section>
<div class="wrap"><div class="layout">
  <div>
    <section><h2>Zadanie</h2><p>{escape(p['problem'])}</p></section>
    <section><h2>Rozwiązanie</h2><p>{escape(p['solution'])}</p></section>
    <section><h2>Wynik</h2><ul class="results">{results}</ul></section>
  </div>
  <aside>
    <div class="box"><h3>Rola</h3><p>{escape(p['role'])}</p></div>
    <div class="box"><h3>Stack</h3><div class="tags">{tags}</div></div>
    {links}
  </aside>
</div></div>
{gallery}
<div class="wrap"><div class="pager">
  <a href="/projekty/{prev_p['slug']}/"><small>Poprzedni</small>{escape(prev_p['title'])}</a>
  <a href="/projekty/{next_p['slug']}/" style="text-align:right"><small>Następny</small>{escape(next_p['title'])}</a>
</div></div>
""" + FOOT + "</body>\n</html>\n"


DIRECTIONS = [
    ("wlasne", "01", "Agenci i automatyzacja AI",
     "Agenci z podziałem ról, którzy pracują w nocy i uczą się na błędach. Głos, twarz 3D, pilot sprzętowy i pulpit, "
     "wszystko na własnej infrastrukturze.", "/projekty/#wlasne", "Systemy własne"),
    ("platformy", "02", "Platformy dla zespołów IT i sieci",
     "Jedna konsola zamiast dziesięciu narzędzi: monitoring, inwentarz, dostęp przez krótkie certyfikaty SSH, "
     "sprawdzane kopie zapasowe i AI, które zna sprzęt.", "/isp/", "Platforma dla operatorów sieci"),
    ("zlecenia", "03", "Zlecenia: sklepy, SEO, dane",
     "Naprawy i wdrożenia dla sklepów internetowych, audyty SEO, bazy firm B2B. Cena z góry, kopia przed zmianą, "
     "rozliczenie przez platformę po odbiorze.", "/uslugi/", "Usługi i cennik"),
]

PRINCIPLES = [
    ("Najpierw dane, potem model",
     "AI dostaje kontekst z własnej bazy: inwentarz, historię, procedury. Dopiero wtedy odpowiada albo działa."),
    ("Kopia przed każdą zmianą",
     "Każda zmiana ma kopię poprzedniego stanu, test wyniku i krótki opis. Odtwarzanie kopii jest sprawdzane, nie zakładane."),
    ("Człowiek zatwierdza",
     "Agent przygotowuje decyzję z wariantami, właściciel wybiera. Nic, co trafia do klienta, nie wychodzi bez akceptacji."),
    ("Własna infrastruktura",
     "Serwer, bazy i modele lokalne tam, gdzie to ma sens. Płatne modele tylko do zadań, w których realnie wygrywają."),
]


def build_home(data: dict) -> str:
    cats = data["categories"]
    projects = data["projects"]
    by_slug = {p["slug"]: p for p in projects}
    featured = [by_slug[s] for s in data.get("featured", [])] or projects[:6]
    counts = {c: sum(1 for p in projects if p["category"] == c) for c in cats}
    dirs = "".join(f"""
      <a class="dir" href="{href}" style="--c:var(--c-{c})">
        <span class="num">{num}</span>
        <h3>{escape(t)}</h3>
        <p>{escape(d)}</p>
        <span class="more">{escape(more)} <span class="n">{counts.get(c, 0)} w katalogu</span> &rarr;</span>
      </a>""" for c, num, t, d, href, more in DIRECTIONS)
    cards = "\n".join(card(p, cats, "h3") for p in featured)
    princ = "".join(f"<li><strong>{escape(a)}</strong><span>{escape(b)}</span></li>" for a, b in PRINCIPLES)
    video = by_slug.get("glowy-agentow", {}).get("video")
    hero_media = (f'<a class="hero-media" href="/projekty/glowy-agentow/" aria-label="Projekt: wirtualne głowy agentów AI">'
                  f'<video src="{escape(video["src"])}" poster="{escape(video.get("poster", ""))}" muted loop playsinline autoplay '
                  f'preload="metadata" width="640" height="316"></video>'
                  f'<span class="cap">Agentka AI mówi własnym głosem, ruch ust z fonemów · <b>projekt &rarr;</b></span></a>') if video else ""
    ld = jsonld({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "GitCloud",
             "alternateName": ["gitcloud.pl", "Git Cloud", "Pracownia AI GitCloud"],
             "url": f"{SITE}/", "inLanguage": "pl-PL", "publisher": {"@id": f"{SITE}/#org"}},
            {"@type": "Organization", "@id": f"{SITE}/#org", "name": "GitCloud", "url": f"{SITE}/",
             "logo": f"{SITE}/favicon-192.png",
             "description": "Pracownia AI: agenci, automatyzacja i platformy dla zespołów IT.",
             "founder": {"@id": f"{SITE}/#aleh"}},
            {"@type": "Person", "@id": f"{SITE}/#aleh", "name": "Aleh Pauliukovich", "url": f"{SITE}/",
             "image": f"{SITE}/img/aleh.jpg", "jobTitle": "Twórca pracowni AI GitCloud",
             "knowsAbout": ["agenci AI", "automatyzacja", "LLM", "monitoring sieci", "Linux", "PostgreSQL",
                            "Python", "ESP32", "Shoper", "SEO"],
             "hasCredential": {"@type": "EducationalOccupationalCredential",
                               "name": "Oracle Cloud Infrastructure Certified AI Foundations Associate",
                               "credentialCategory": "certification",
                               "recognizedBy": {"@type": "Organization", "name": "Oracle"}},
             "worksFor": {"@id": f"{SITE}/#org"}},
            {"@type": "ItemList", "name": "Wybrane projekty", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/projekty/{p['slug']}/", "name": p["title"]}
                for i, p in enumerate(featured)]},
        ],
    })
    title = "GitCloud: pracownia AI. Agenci, automatyzacja, platformy | Aleh Pauliukovich"
    desc = ("Pracownia AI Aleha Pauliukovicha: agenci AI, automatyzacja, platformy dla zespołów IT i sieci, "
            "zlecenia dla sklepów internetowych. Katalog projektów z zadaniem, rozwiązaniem i wynikiem.")
    # stare kotwice landingu ISP (gitcloud.pl/#platforma, #faq …) prowadzą teraz na /isp/#…
    old_anchors = ('<script>(function(){var h=location.hash.slice(1);'
                   'if(/^(platforma|mozliwosci|faq|zalozyciel|stat-grid|sw-[a-z]+)$/.test(h))'
                   'location.replace("/isp/#"+h)})();</script>\n')
    return head(title, desc, "/", old_anchors + ld, OG_DEFAULT, active="/").replace(
        "<main>", '<main class="home">', 1) + f"""<section class="hero home-hero">
  <div class="wrap hero-grid">
    <div>
      <div class="kicker">Pracownia AI · Aleh Pauliukovich</div>
      <h1>Buduję systemy z AI w środku, które <span class="hl">działają same</span> i dają się sprawdzić.</h1>
      <p class="lead">Agenci, którzy w nocy rozwiązują alarmy serwera. Platforma, w której zespół sieciowy widzi całą sieć w jednym miejscu. Naprawy sklepów internetowych z testem na każdej domenie. Wszystko projektuję, piszę i utrzymuję sam.</p>
      <div class="actions">
        <a class="btn btn-primary" href="/projekty/">Zobacz projekty</a>
        <a class="btn btn-ghost" href="#kontakt">Kontakt</a>
      </div>
    </div>
    {hero_media}
  </div>
  <div class="wrap">
    <ul class="facts">
      <li><b>{len(projects)}</b><span>projektów w katalogu, z wynikiem w liczbach</span></li>
      <li><b>3</b><span>agentów AI w codziennej pracy, także w nocy</span></li>
      <li><b>4+</b><span>lata w administracji IT: serwery, sieci, Microsoft 365</span></li>
      <li><b>98%</b><span>egzamin Oracle OCI AI Foundations Associate</span></li>
    </ul>
  </div>
</section>

<section class="band" id="kierunki">
  <div class="wrap">
    <div class="kicker">Czym się zajmuję</div>
    <h2 class="sec-title">Trzy kierunki pracowni</h2>
    <div class="dirs">{dirs}
    </div>
  </div>
</section>

<section class="band" id="projekty">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <div class="kicker">Wybrane projekty</div>
        <h2 class="sec-title">Co już działa</h2>
      </div>
      <a class="link-all" href="/projekty/">Cały katalog ({len(projects)}) &rarr;</a>
    </div>
    <div class="grid home-grid">
{cards}
    </div>
  </div>
</section>

<section class="band" id="zasady">
  <div class="wrap">
    <div class="kicker">Jak pracuję</div>
    <h2 class="sec-title">Cztery zasady w każdym projekcie</h2>
    <ol class="principles">{princ}</ol>
  </div>
</section>

<section class="band" id="o-mnie">
  <div class="wrap who">
    <img src="/img/aleh.jpg" alt="Aleh Pauliukovich" width="200" height="200" loading="lazy">
    <div>
      <div class="kicker">Kto prowadzi pracownię</div>
      <h2 class="sec-title">Aleh Pauliukovich</h2>
      <p>Administrator IT z ponad czteroletnim doświadczeniem: Windows Server i Active Directory, Microsoft 365 i Intune, Linux i Docker, sieci i VPN, automatyzacja w Pythonie i PowerShellu. Pracowałem zarówno zdalnie, jak i przy wdrożeniach na miejscu.</p>
      <p>W pracowni łączę to z AI: modele językowe, rozpoznawanie mowy, agenci z pamięcią decyzji w PostgreSQL, firmware na ESP32. Certyfikat Oracle Cloud Infrastructure AI Foundations Associate (2026).</p>
    </div>
  </div>
</section>

<section class="band cta" id="kontakt">
  <div class="wrap cta-grid">
    <div>
      <h2 class="sec-title">Masz proces, który da się zautomatyzować?</h2>
      <p>Opisz go w kilku zdaniach: co dziś robi się ręcznie, ile to trwa i co jest wynikiem. Odpowiem, czy i jak to zrobić, zanim padnie jakakolwiek cena.</p>
    </div>
    <div class="contact-card">
      <div class="ct-label">// kontakt</div>
      <p>E-mail i zasady współpracy są na stronie usług. Małe zlecenia (sklepy, poczta, serwery) mają cennik z góry.</p>
      <a class="btn btn-primary" href="/uslugi/#kontakt">Napisz wiadomość &rarr;</a>
      <a class="btn btn-ghost" href="/uslugi/#cennik">Cennik</a>
    </div>
  </div>
</section>
""" + FOOT + "</body>\n</html>\n"


def sitemap(projects: list[dict], today: str) -> str:
    base = [("/", "weekly", "1.0"), ("/projekty/", "weekly", "0.9"), ("/uslugi/", "monthly", "0.9"),
            ("/isp/", "monthly", "0.8"),
            ("/privacy.html", "yearly", "0.3")]
    base += [(f"/projekty/{p['slug']}/", "monthly", "0.7") for p in projects]
    rows = "".join(f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{today}</lastmod>\n"
                   f"    <changefreq>{f}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n" for u, f, pr in base)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + rows + "</urlset>\n")


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    errs = validate(data)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    if "--check" in sys.argv:
        print(f"ok: {len(data['projects'])} projektów")
        return 0
    pages = {OUT / "index.html": build_index(data), ROOT / "index.html": build_home(data)}
    for i, p in enumerate(data["projects"]):
        pages[OUT / p["slug"] / "index.html"] = build_page(data, i)
    for path, html in pages.items():
        e = problems_in(html, str(path.relative_to(ROOT)))
        if e:
            print("\n".join(e), file=sys.stderr)
            return 1
    # usuń strony projektów, których nie ma już w danych
    keep = {p["slug"] for p in data["projects"]}
    if OUT.is_dir():
        for d in OUT.iterdir():
            if d.is_dir() and d.name not in keep and (d / "index.html").is_file():
                (d / "index.html").unlink()
                d.rmdir()
    for path, html in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    today = date.today().isoformat()
    (ROOT / "sitemap.xml").write_text(sitemap(data["projects"], today), encoding="utf-8")
    print(f"ok: {len(pages)} stron, sitemap {today}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
