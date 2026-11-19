#!/usr/bin/env python3
"""Cvety i materiały strony z rdzenia GitCloud (07.11.2026, decyzja #692 „strona jako część ekosystemu”).

Źródło: gitcloud-core — gitcloud_core/static/palette.json (kolory, wyjście tools/palette, decyzja #690) i tokens.css
(materiały „jednego światła z góry”: krawędź szkła, nisza, wypukłość). Wynik: src/styles/core.css z --gc-* — strona
bierze z niego kolory w site.css, własnych kolorów palety liczbą nie wpisuje. Plik generowany jest w repo, bo build na
GitHub Actions rdzenia nie widzi.

  tools/tokeny.py            przebuduj src/styles/core.css      (GC_CORE=ścieżka do gitcloud-core, domyślnie ~/src/gitcloud-core)
  tools/tokeny.py --check    kod 1, gdy core.css rozszedł się z rdzeniem (noc: home-sync)
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = Path(os.environ.get("GC_CORE", Path.home() / "src/gitcloud-core"))
OUT = ROOT / "src/styles/core.css"
THEMES = ROOT / "src/data/themes.json"   # 19.11.2026: konfig motywów rdzenia dla przycisku (Base.astro)

COLORS = ["bg-deep", "fg", "muted", "card", "edge", "neon", "magenta", "c-ok", "c-ok-t", "c-warn", "c-crit"]
# 11.11.2026 (właściciel: «скроллер — один стиль во всей экосистеме»): pasek przewijania z rdzenia — tokeny --sb-*
# (rozwinięte do liczb palety) i reguły scroll.css (var(--sb-*) → var(--gc-sb-*)); strona własnego paska nie pisze
SCROLL = ["sb-size", "sb-inset", "sb-thumb-w", "sb-thumb", "sb-thumb-hover", "sb-color"]
MATERIALS = ["rim-top", "well", "well-top", "well-bot", "bevel-face", "sink", "hi-1", "lift-btn", "lift-sel"]


def tokens(css: str) -> dict:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    out = {}
    for sel, body in re.findall(r"(:root(?:\[data-theme=\"neo\"\])?)\s*\{(.*?)\}", css, flags=re.DOTALL):
        for k, v in re.findall(r"--([a-z0-9-]+)\s*:\s*([^;]+);", body):
            out[k] = " ".join(v.split())
    return out


def tokens_tone(css: str, tone: str) -> dict:
    """Motyw z konfigu rdzenia (themes.json): blok :root[data-theme="neo"][data-tone="<motyw>"] na „Neo”."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    m = re.search(r':root\[data-theme="neo"\]\[data-tone="' + re.escape(tone) + r'"\]\s*\{(.*?)\}', css, flags=re.DOTALL)
    return {k: " ".join(v.split()) for k, v in re.findall(r"--([a-z0-9-]+)\s*:\s*([^;]+);", m.group(1) if m else "")}


def block(pal: dict, tok: dict) -> list:
    """Zmienne --gc-* jednego tonu: kolory z palety, materiały i pasek przewijania z tokenów (rozwinięte do liczb)."""
    lines = []
    for k in COLORS:
        h = pal[k]
        lines.append(f"  --gc-{k}:{h}; --gc-{k}-rgb:{int(h[1:3], 16)},{int(h[3:5], 16)},{int(h[5:7], 16)};")
    for k in MATERIALS:
        v = re.sub(r"linear-gradient\(var\(--fg\), var\(--fg\)\)[^,]*no-repeat,\s*", "", tok[k])   # засечка панели — nie na stronie
        if "var(" in v:
            raise SystemExit(f"tokeny: --{k} zależy od innej zmiennej ({v}) — dopisz rozwinięcie")
        lines.append(f"  --gc-{k}:{v};")
    rgb = {f"{k}-rgb": f"{int(pal[k][1:3], 16)},{int(pal[k][3:5], 16)},{int(pal[k][5:7], 16)}" for k in ("neon", "magenta")}
    for k in SCROLL:
        v = re.sub(r"var\(--(neon-rgb|magenta-rgb)\)", lambda m: rgb[m.group(1)], tok[k])
        v = re.sub(r"var\(--(sb-[a-z-]+)\)", r"var(--gc-\1)", v)
        if re.search(r"var\(--(?!gc-sb-)", v):
            raise SystemExit(f"tokeny: --{k} zależy od innej zmiennej ({v}) — dopisz rozwinięcie")
        lines.append(f"  --gc-{k}:{v};")
    return lines


def render() -> str:
    pal = json.loads((CORE / "gitcloud_core/static/palette.json").read_text(encoding="utf-8"))
    css = (CORE / "gitcloud_core/static/tokens.css").read_text(encoding="utf-8")
    tok = tokens(css)
    lines = ["/* Wygenerowane: tools/tokeny.py z gitcloud-core (palette.json + tokens.css), decyzja #692. Nie edytować ręcznie. */", ":root{"]
    lines += block(pal, tok)
    lines.append("}")
    # 19.11.2026 (właściciel: «pełny konfig motywów na przyszłość»): każdy motyw konfigu rdzenia (themes.json) — kolory
    # palette-tones.json i blok data-tone z tokens.css; stronę przełącza html[data-tone] (Base.astro: wybór gościa albo system)
    for t, tpal in json.loads((CORE / "gitcloud_core/static/palette-tones.json").read_text(encoding="utf-8")).items():
        lines.append(f':root[data-tone="{t}"]{{')
        lines += block(tpal, {**tok, **tokens_tone(css, t)})
        lines.append("}")
    sc = re.sub(r"/\*.*?\*/\s*", "", (CORE / "gitcloud_core/static/scroll.css").read_text(encoding="utf-8"), flags=re.DOTALL)
    sc = sc[:sc.index(".gc-scroll{")] if ".gc-scroll{" in sc else sc      # pasek dokumentu my.gitcloud.pl (app.js) — nie na stronie
    sc = re.sub(r"var\(--(sb-[a-z-]+)\)", r"var(--gc-\1)", sc).replace("var(--r-pill)", "999px")
    if re.search(r"var\(--(?!gc-)", sc):
        raise SystemExit("tokeny: scroll.css rdzenia używa zmiennej spoza --sb-* — dopisz rozwinięcie")
    lines.append("/* pasek przewijania — scroll.css rdzenia */")
    lines.append(sc.strip())
    return "\n".join(lines) + "\n"


def themes() -> str:
    """Konfig motywów rdzenia dla przycisku strony (Base.astro): kolejność, motyw bazowy, ikony."""
    c = json.loads((CORE / "gitcloud_core/themes.json").read_text(encoding="utf-8"))
    return json.dumps({"base": c["base"], "order": c["order"], "icons": {k: v["icon"] for k, v in c["themes"].items()}},
                      ensure_ascii=False, indent=1) + "\n"


def main() -> int:
    text = render()
    th = themes()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text and THEMES.exists() and THEMES.read_text(encoding="utf-8") == th
        print("tokeny: core.css zgodny z rdzeniem" if ok else "tokeny: core.css rozszedł się z rdzeniem — uruchom tools/tokeny.py i wypuść stronę")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    THEMES.write_text(th, encoding="utf-8")
    print(f"tokeny: {OUT.relative_to(ROOT)} ({len(COLORS)} kolorów, {len(MATERIALS)} materiałów, pasek przewijania)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
