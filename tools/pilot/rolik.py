#!/usr/bin/env python3
"""Film pilota ESP32 na stronę (public/img/projekty/pilot.mp4 + pilot-wideo.jpg).

To samo co render.py (kopia firmware i symulatora, napisy PL, dane przykładowe), plus w kopii sim.cpp:
polecenie scenariusza «rec 1/0» zapisuje ekran co 40 ms czasu wirtualnego (25 kl./s) do katalogu klatek.
Klatki 320×170 → 3× piksel w piksel (960×510) → ffmpeg H.264, bez dźwięku.

Uruchomienie: ~/job-hunter/.venv/bin/python -I tools/pilot/rolik.py [KATALOG_KLATEK]
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

HERE = render.HERE
OUT = render.OUT
FPS = 25

EXTRA_PL = [
    ("pilot.h", '"Проверяю…"', '"Sprawdzam…"'),
    ("main.cpp", '"клик: график"', '"klik: wykres"'),
    ("charts.h", 'emptyState(x0, top, "Загружаю"', 'emptyState(x0, top, "Wczytuję"'),
]

# zapis klatek w kopii symulatora (repozytorium pilota się nie zmienia)
SIM_PATCH = [
    ("static void run(unsigned long ms) {",
     "static void png(const std::string& path);\n"
     "static bool recOn = false; static std::string recDir; static uint64_t recNext = 0; static int recN = 0;\n"
     "static void recTick() {\n"
     "  if (!recOn) return;\n"
     "  while (now_us >= recNext) { char b[32]; snprintf(b, sizeof b, \"/%05d.png\", recN++); png(recDir + b); recNext += 40000; }\n"
     "}\n"
     "static void run(unsigned long ms) {"),
    ("while (now_us < end) { uint64_t t = now_us; loop(); if (now_us == t) now_us += 1000; }",
     "while (now_us < end) { uint64_t t = now_us; loop(); if (now_us == t) now_us += 1000; recTick(); }"),
    ('else if (cmd == "wait") run(atoi(rest.c_str()));',
     'else if (cmd == "wait") run(atoi(rest.c_str()));\n'
     '    else if (cmd == "rec") { recOn = atoi(rest.c_str()) != 0; recDir = out + "/frames"; recNext = now_us; }'),
]


def main():
    keep = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    tmp = Path(tempfile.mkdtemp(prefix="pilot-rolik-"))
    try:
        sim = render.prepare(tmp, (HERE / "rolik.txt").read_text(), EXTRA_PL)
        p = sim / "sim.cpp"
        t = p.read_text()
        for a, b in SIM_PATCH:
            if a not in t:
                sys.exit(f"sim.cpp: nie ma «{a[:60]}» : symulator się zmienił, popraw SIM_PATCH")
            t = t.replace(a, b, 1)
        p.write_text(t)
        subprocess.run(["./build.sh"], cwd=sim, check=True, stdout=subprocess.DEVNULL)
        (sim / "out/frames").mkdir(parents=True)
        subprocess.run(["build/gc-sim", "pl.txt", "out"], cwd=sim, check=True, stdout=subprocess.DEVNULL)
        frames = sim / "out/frames"
        n = len(list(frames.glob("*.png")))
        print("klatki:", n, f"({n / FPS:.1f} s)")
        if keep:
            shutil.rmtree(keep, ignore_errors=True)
            shutil.copytree(frames, keep)
        mp4 = OUT / "pilot.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", str(frames / "%05d.png"),
                        "-vf", "scale=iw*3:ih*3:flags=neighbor,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
                        "-crf", "28", "-tune", "animation", "-movflags", "+faststart", "-an", str(mp4)], check=True)
        jpg = OUT / "pilot-wideo.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(frames / f"{2 * FPS:05d}.png"),
                        "-vf", "scale=iw*3:ih*3:flags=neighbor", "-q:v", "3", str(jpg)], check=True)
        for f in (mp4, jpg):
            print(f.relative_to(render.SITE), f.stat().st_size // 1024, "KB")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
