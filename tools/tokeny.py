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

COLORS = ["bg-deep", "fg", "muted", "card", "edge", "neon", "magenta", "c-ok", "c-ok-t", "c-warn", "c-crit"]
MATERIALS = ["rim-top", "well", "well-top", "well-bot", "bevel-face", "sink", "hi-1", "lift-btn", "lift-sel"]


def tokens(css: str) -> dict:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    out = {}
    for sel, body in re.findall(r"(:root(?:\[data-theme=\"neo\"\])?)\s*\{(.*?)\}", css, flags=re.DOTALL):
        for k, v in re.findall(r"--([a-z0-9-]+)\s*:\s*([^;]+);", body):
            out[k] = " ".join(v.split())
    return out


def render() -> str:
    pal = json.loads((CORE / "gitcloud_core/static/palette.json").read_text(encoding="utf-8"))
    tok = tokens((CORE / "gitcloud_core/static/tokens.css").read_text(encoding="utf-8"))
    lines = ["/* Wygenerowane: tools/tokeny.py z gitcloud-core (palette.json + tokens.css), decyzja #692. Nie edytować ręcznie. */", ":root{"]
    for k in COLORS:
        h = pal[k]
        lines.append(f"  --gc-{k}:{h}; --gc-{k}-rgb:{int(h[1:3], 16)},{int(h[3:5], 16)},{int(h[5:7], 16)};")
    for k in MATERIALS:
        v = tok[k]
        if "var(" in v:
            raise SystemExit(f"tokeny: --{k} zależy od innej zmiennej ({v}) — dopisz rozwinięcie")
        lines.append(f"  --gc-{k}:{v};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("tokeny: core.css zgodny z rdzeniem" if ok else "tokeny: core.css rozszedł się z rdzeniem — uruchom tools/tokeny.py i wypuść stronę")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"tokeny: {OUT.relative_to(ROOT)} ({len(COLORS)} kolorów, {len(MATERIALS)} materiałów)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
