"""Głowy agentów: klatki 1:1 z clip.py → animowane WebP do sekcji „Agenci”, filmy 2:1 i plakaty do projektu „Awatary 3D”.

Uruchomienie: ~/job-hunter/.venv/bin/python -I tools/glowy/wyjscie.py <katalog klatek clip.py> [katalog roboczy]
Klatki <who>_NNN.png (kwadrat, głowa z ramionami i piersią) — fr() przycina do ramion (PLECY). Kadry filmów stoją ramionami na dolnej krawędzi,
żeby tors nie wisiał w powietrzu; tło jak w head.js (5, 7, 11).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

SITE = Path(__file__).resolve().parents[2] / "public/img"
C = Path(sys.argv[1])
T = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.mkdtemp(prefix="glowy-"))
BG = (5, 7, 11)
N = 99   # 6,6 s × 15 kl./s
WHO = [("sally", "sally"), ("vale", "tony"), ("mark", "mark")]


# 13.11.2026 (właściciel: «wszędzie tylko do ramion, torsu niżej nigdzie»): z kadru clip.py (głowa z ramionami i piersią)
# wycinamy kwadrat od czubka do linii ramion — w ułamkach boku, ta sama wysokość głów u wszystkich trzech
PLECY = (0.11, 0.03, 0.89, 0.81)


def fr(w, i):
    im = Image.open(C / f"{w}_{i:03d}.png").convert("RGB")
    x0, y0, x1, y1 = PLECY
    return im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))


def single(w, i):   # 960×474: głowa z ramionami pośrodku
    c = Image.new("RGB", (960, 474), BG)
    c.paste(fr(w, i).resize((474, 474), Image.LANCZOS), (243, 0))
    return c


TRIO_S, TRIO_DX = 520, 400   # trójka 1280×632: kwadraty 560 px stoją na dolnej krawędzi; ramiona zachodzą na siebie,
                              # Tony pośrodku z przodu (maska: wszystko, co nie jest tłem)


def trio(i):
    c = Image.new("RGB", (1280, 632), BG)
    for k in (0, 2, 1):
        h = fr(WHO[k][0], i).resize((TRIO_S, TRIO_S), Image.LANCZOS)
        mask = Image.eval(ImageChops.difference(h, Image.new("RGB", h.size, BG)).convert("L"), lambda v: 255 if v > 2 else 0)
        c.paste(h, (640 + (k - 1) * TRIO_DX - TRIO_S // 2, 632 - TRIO_S), mask)
    return c


# 1) animowane WebP 360 px (sekcja pokazuje do 320 px, na ekranach 2x wystarcza)
for w, n in WHO:
    fs = [fr(w, i).resize((360, 360), Image.LANCZOS) for i in range(N)]
    fs[0].save(SITE / f"agenci/{n}.webp", save_all=True, append_images=fs[1:], duration=67, loop=0, quality=48, method=6)
    print(n, os.path.getsize(SITE / f"agenci/{n}.webp") // 1024, "KB")

# 2) filmy i plakaty (plakat = pierwsza klatka: film startuje bez skoku, wszyscy z otwartymi oczami)
jobs = [(f"glowa-{n}", lambda i, w=w: single(w, i)) for w, n in WHO] + [("glowy", trio)]
for name, mk in jobs:
    d = T / name
    d.mkdir(parents=True, exist_ok=True)
    for i in range(N):
        mk(i).save(d / f"{i:03d}.png")
    mp4 = SITE / f"projekty/{name}.mp4"
    subprocess.run(["nice", "-n", "19", "ffmpeg", "-y", "-loglevel", "error", "-threads", "2", "-framerate", "15",
                    "-i", str(d / "%03d.png"), "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-an", str(mp4)], check=True)
    mk(0).save(SITE / f"projekty/{name}.jpg", quality=86)
    print(name, mp4.stat().st_size // 1024, "KB")
