#!/usr/bin/env python3
"""Zrzuty pilota ESP32 po polsku na stronę (public/img/projekty/pilot-*.png).

Pilot na co dzień mówi po rosyjsku, a jego firmware się tu NIE zmienia. Skrypt:
1. kopiuje firmware/ i sim/ z repozytorium pilota (GC_REMOTE, domyślnie ~/src/gitcloud-remote) do katalogu tymczasowego,
2. w kopii podmienia napisy widoczne na sześciu ekranach na polskie (PL niżej; brak trafienia = błąd),
3. bierze dane wzorcowe symulatora (sim/fixtures/golden.jsonl, poza tym repo) i nadpisuje wszystko, co widać
   na zrzutach, danymi przykładowymi (DEMO niżej): wymyślone usługi, utwór, polecenie,
4. buduje symulator, odgrywa scenariusz.txt i zapisuje ekrany 320×170 powiększone 4× (piksel w piksel).

Uruchomienie: ~/job-hunter/.venv/bin/python -I tools/pilot/render.py   (Pillow; symulator: g++, zlib)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
REMOTE = Path(os.environ.get("GC_REMOTE", Path.home() / "src/gitcloud-remote"))
OUT = SITE / "public/img/projekty"
SHOTS = ["kafelki", "claude", "muzyka", "wykres", "maszyny", "pin"]

# (plik, było, jest) : tylko kopia w katalogu tymczasowym
PL = [
    ("statusbar.h", '{"вс", "пн", "вт", "ср", "чт", "пт", "сб"}', '{"nd", "pn", "wt", "śr", "cz", "pt", "sb"}'),
    ("statusbar.h", '{"янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"}',
     '{"sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"}'),
    ("claude.h", '"Сессия готова"', '"Sesja gotowa"'),
    ("claude.h", '"Клик ручки: говори, клик: отправить"', '"Klik pokrętła: mów, klik: wyślij"'),
    ("claude.h", '"удержание: меню сессии"', '"przytrzymanie: menu sesji"'),
    ("claude.h", 's = "работает"', 's = "pracuje"'),
    ("claude.h", '"5ч %d%%" : "5ч -"', '"5h %d%%" : "5h -"'),
    ("claude.h", '"нед. %d%%" : "нед. -"', '"tydz. %d%%" : "tydz. -"'),
    ("nowplaying.h", '"ИГРАЕТ" : "ПАУЗА"', '"GRA" : "PAUZA"'),
    ("charts.h", '{"15 мин", "1 ч", "6 ч", "24 ч", "7 дней", "30 дней"}', '{"15 min", "1 h", "6 h", "24 h", "7 dni", "30 dni"}'),
    ("charts.h", '" · 2×: дальше"', '" · 2×: dalej"'),
    ("guests_ha.h", 'String("выключена")', 'String("wyłączona")'),
    ("pilot.h", '"ручка: цифра · клик: дальше · боковая: отмена"', '"pokrętło: cyfra · klik: dalej · boczny: anuluj"'),
]

# dane przykładowe: zastępują wiadomości o tym samym typie «t»
DEMO = {
    "np": {"t": "np", "on": True, "pl": False, "ti": "Lo-fi do pracy", "ar": "", "al": "",
           "len": 3540, "pos": 2310, "src": "Muzyka", "yt": 0},
    "gl": {"t": "gl", "r": [[0, 100, "app-web", 1, 3, 1840, 4096], [1, 101, "automatyzacje", 0, 0, 0, 2048],
                            [1, 102, "PostgreSQL", 1, 1, 410, 2048], [1, 103, "sejf-hasel", 1, 0, 96, 512],
                            [0, 104, "zapora", 1, 2, 2100, 4096], [1, 105, "harmonogram", 1, 0, 280, 1024]]},
}
PIN_CMD = "Restart zapory"


def main():
    if not (REMOTE / "sim/fixtures/golden.jsonl").exists():
        sys.exit(f"brak {REMOTE}/sim/fixtures/golden.jsonl")
    tmp = Path(tempfile.mkdtemp(prefix="pilot-pl-"))
    try:
        shutil.copytree(REMOTE / "firmware", tmp / "firmware", ignore=shutil.ignore_patterns(".pio"))
        sim = tmp / "sim"
        sim.mkdir()
        for n in ("build.sh", "sim.cpp", "fw.cpp"):
            shutil.copy2(REMOTE / "sim" / n, sim / n)
        shutil.copytree(REMOTE / "sim/stubs", sim / "stubs")
        if (REMOTE / "sim/build").exists():                       # skompilowane biblioteki: szybciej
            shutil.copytree(REMOTE / "sim/build", sim / "build")
        (sim / ".deps").symlink_to(REMOTE / "sim/.deps")

        src = tmp / "firmware/src"
        for f, a, b in PL:
            p = src / f
            t = p.read_text()
            if a not in t:
                sys.exit(f"{f}: nie ma «{a}» : firmware się zmienił, popraw listę PL")
            p.write_text(t.replace(a, b))

        lines = []
        for l in (REMOTE / "sim/fixtures/golden.jsonl").read_text().splitlines():
            if l.strip() and json.loads(l).get("t") in DEMO:
                continue
            lines.append(l)
        lines += [json.dumps(m, ensure_ascii=False) for m in DEMO.values()]
        (sim / "data.jsonl").write_text("\n".join(lines) + "\n")
        scen = (HERE / "scenariusz.txt").read_text().replace("@PIN@", PIN_CMD)
        (sim / "pl.txt").write_text(scen)

        subprocess.run(["./build.sh"], cwd=sim, check=True, stdout=subprocess.DEVNULL)
        (sim / "out").mkdir()
        subprocess.run(["build/gc-sim", "pl.txt", "out"], cwd=sim, check=True, stdout=subprocess.DEVNULL)
        for s in SHOTS:
            im = Image.open(sim / "out" / f"{s}.png").convert("RGB")
            im = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
            dst = OUT / f"pilot-{s}.png"
            im.save(dst, optimize=True)
            print(dst.relative_to(SITE), dst.stat().st_size // 1024, "KB")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
