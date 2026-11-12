#!/usr/bin/env python3
"""Film „Pulpit GitCloud” (README.md): scenariusz w sesji z sesja.sh, klatki grim (z kursorem) → koduj() z panel-demo.

  python3 tools/pulpit/scenariusz.py KATALOG_KLATEK            nagranie → public/img/projekty/pulpit.mp4 + pulpit-wideo.jpg
  ZRZUTY=KAT python3 … KATALOG_KLATEK                         nagranie + pełne zrzuty PNG w punktach scenariusza (galeria)
  python3 tools/pulpit/scenariusz.py KATALOG_KLATEK --kroki    bez filmu: jedna klatka PNG po każdym kroku (do strojenia)

Kursor i kliknięcia: `swaymsg seat seat0 cursor …` (headless nie ma urządzeń wejścia). Klatki PPM w pełnej rozdzielczości
(grim bywa bez JPEG, a jego skalowanie jest wolne), zmniejszane przy kodowaniu; czasy klatek w meta.json jak w screencaście panelu."""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "panel-demo"))
D = Path(os.environ.get("PULPIT_DIR", Path.home() / ".cache/gitcloud/pulpit-demo"))
ENV = dict(x.split("=", 1) for x in open(D / "env").read().split()[1:])
H = ENV["HOME_DEMO"]
R = ENV["XDG_RUNTIME_DIR"]
E = {"HOME": H, "USER": os.environ["USER"], "PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8",
     "XDG_RUNTIME_DIR": R, "SWAYSOCK": ENV["SWAYSOCK"], "WAYLAND_DISPLAY": ENV["WAYLAND_DISPLAY"],
     "DBUS_SESSION_BUS_ADDRESS": open(f"{R}/pd-bus").read().strip(), "NO_AT_BRIDGE": "1", "GTK_A11Y": "none",
     "GC_CONSOLE_PORT": "18779", "GC_CONSOLE_TMUX": "pulpit-demo", "GC_FILES_PORT": "18781"}
BIN = f"{H}/.config/gitcloud-desk/bin"
OUT = Path(sys.argv[1])
KROKI = "--kroki" in sys.argv
OUT.mkdir(parents=True, exist_ok=True)


def sh(*cmd, bg=False):
    if bg:
        return subprocess.Popen(cmd, env=E, cwd=H, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return subprocess.run(cmd, env=E, cwd=H, capture_output=True, text=True, timeout=30).stdout


def sway(c):
    return sh("swaymsg", c)


def tree():
    return json.loads(sh("swaymsg", "-t", "get_tree", "-r") or "{}")


def win(app):
    """→ prostokąt okna (x, y, w, h) po app_id albo None."""
    st = [tree()]
    while st:
        n = st.pop()
        if n.get("app_id") == app and n.get("visible"):
            r = n["rect"]
            return r["x"], r["y"], r["width"], r["height"]
        st += n.get("nodes", []) + n.get("floating_nodes", [])
    return None


def wait_win(app, t=20):
    end = time.time() + t
    while time.time() < end:
        if (r := win(app)):
            return r
        time.sleep(0.2)
    raise SystemExit(f"okno {app} nie pojawiło się")


CUR = [960, 540]


def move(x, y, s=0.6):
    """Płynny ruch kursora."""
    x0, y0 = CUR
    n = max(1, int(s * 30))
    for i in range(1, n + 1):
        k = i / n
        k = k * k * (3 - 2 * k)
        sway(f"seat seat0 cursor set {round(x0 + (x - x0) * k)} {round(y0 + (y - y0) * k)}")
        time.sleep(s / n)
    CUR[:] = [x, y]


def click(x, y, s=0.6):
    move(x, y, s)
    sway("seat seat0 cursor press button1")
    time.sleep(0.08)
    sway("seat seat0 cursor release button1")


def push(title):
    """Powiadomienie GitCloud: ta sama droga co push z panelu (notify-send → serwer powiadomień paska); → id do zamknięcia.
    Dymek pasek pokazuje tylko dla pilnych, a pilny sam nie znika."""
    return sh("notify-send", "-p", "-a", "GitCloud", "-u", "critical", title).strip()


def zamknij_push(nid):
    sh("gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications", "--object-path", "/org/freedesktop/Notifications",
       "--method", "org.freedesktop.Notifications.CloseNotification", nid)


def przesun(app, dx, dy, s=0.9):
    """Przeciągnięcie okna za nagłówek: kursor na nagłówku, okno jedzie razem z nim (sway move position)."""
    x, y, w, h = win(app)
    hx, hy = x + w // 2, y + 14
    move(hx, hy, 0.5)
    sway("seat seat0 cursor press button1")
    n = max(1, int(s * 30))
    for i in range(1, n + 1):
        k = i / n
        k = k * k * (3 - 2 * k)
        sway(f'[app_id="{app}"] move position {round(x + dx * k)} {round(y + dy * k)}')
        sway(f"seat seat0 cursor set {round(hx + dx * k)} {round(hy + dy * k)}")
        time.sleep(s / n)
    sway("seat seat0 cursor release button1")
    CUR[:] = [hx + dx, hy + dy]


def wpisz(text, cps=14):
    """Pisanie w pierwszej karcie konsoli (WebSocket serwera kart, ten sam token co okno)."""
    import asyncio
    import aiohttp
    tok = open(f"{H}/.config/gitcloud-desk/console/token").read().strip()
    base = f"http://127.0.0.1:{E['GC_CONSOLE_PORT']}"

    async def go():
        async with aiohttp.ClientSession(headers={"X-Console-Token": tok}) as s:
            async with s.get(f"{base}/api/tabs") as r:
                tab = (await r.json())[0]["id"]
            async with s.ws_connect(f"{base}/ws/tab/{tab}") as ws:
                for ch in text:
                    await ws.send_str(json.dumps({"t": "in", "d": ch}))
                    await asyncio.sleep(1 / cps)
                await asyncio.sleep(0.3)
    asyncio.run(go())


# ── klatki ──
frames, stop = [], threading.Event()
T0 = [0.0]


def capture():
    i = 0
    while not stop.is_set():
        t = time.time() - T0[0]
        f = OUT / f"f{i:05d}.ppm"                    # grim bez JPEG i z wolnym skalowaniem: PPM 1920×1080, ok. 18 klatek/s
        if subprocess.run(["grim", "-c", "-t", "ppm", str(f)], env=E, timeout=10).returncode == 0:
            frames.append([round(t, 3), str(f)])
            i += 1
        time.sleep(max(0.0, 0.04 - (time.time() - T0[0] - t)))


n_krok = [0]


def krok(name, hold=0.0):
    """Punkt scenariusza: w trybie --kroki zrzut PNG, w nagraniu — pauza hold sekund."""
    if KROKI:
        time.sleep(max(hold, 1.0))
        n_krok[0] += 1
        subprocess.run(["grim", "-c", str(OUT / f"k{n_krok[0]:02d}-{name}.png")], env=E, timeout=10)
        print("krok", n_krok[0], name, flush=True)
    else:
        if (z := os.environ.get("ZRZUTY")):           # pełne zrzuty PNG do galerii w połowie punktu (okno zdążyło się narysować)
            time.sleep(hold / 2)
            Path(z).mkdir(parents=True, exist_ok=True)
            subprocess.run(["grim", "-c", f"{z}/{name}.png"], env=E, timeout=10)
            time.sleep(hold / 2)
        else:
            time.sleep(hold)


def scenariusz():
    # 1. pulpit: miasto w deszczu wieczorem, panel po lewej, konsola po prawej, pod spodem podłoga w rytm muzyki
    move(1500, 600, 0.1)
    krok("pulpit", 2.0)
    wpisz("cd Projekty/katalog-www && git log --oneline\r")
    krok("konsola", 1.5)
    # 2. powiadomienie GitCloud na pasku
    nid = push("Kopia zapasowa gotowa: 7 maszyn, sprawdzenie ok")
    krok("push", 3.2)
    zamknij_push(nid)
    # 3. Pliki w ramce GitCloud: otwarcie, przeciągnięcie za nagłówek, rozwinięcie i powrót
    sh(f"{BIN}/desk-url", "files", bg=True)
    x, y, w, h = wait_win("pl.gitcloud.Files")
    krok("pliki", 1.6)
    przesun("pl.gitcloud.Files", 420, 90, 1.0)
    krok("przeciagniete", 0.8)
    x, y, w, h = win("pl.gitcloud.Files")
    przesun("pl.gitcloud.Files", 0, 30 - y, 0.6)       # do górnej krawędzi — przyklejenie: rozwinięcie na cały pulpit
    sh(f"{BIN}/desk-url", "max", "files")
    krok("rozwiniete", 1.6)
    sh(f"{BIN}/desk-url", "max", "files")
    krok("przywrocone", 1.0)
    # 4. zdjęcie w GitCloud Foto
    sh(f"{BIN}/gitcloud-photos", "window", f"{H}/Obrazy/ekran-scena-1.webp", bg=True)
    wait_win("pl.gitcloud.Photos")
    krok("foto", 2.4)
    sh(f"{BIN}/desk-url", "hide")
    # 5. szybkie wyszukiwanie na pasku, potem GitCloud Media z filmem
    sh("gdbus", "call", "--session", "--dest", "pl.gitcloud.Bar", "--object-path", "/pl/gitcloud/Bar", "--method", "pl.gitcloud.Bar.Launcher")
    krok("szukaj", 2.2)
    sh("gdbus", "call", "--session", "--dest", "pl.gitcloud.Bar", "--object-path", "/pl/gitcloud/Bar", "--method", "pl.gitcloud.Bar.Launcher")
    sh(f"{BIN}/gitcloud-media", "window", f"{H}/Wideo/awatary.mp4", bg=True)
    wait_win("pl.gitcloud.Media")
    krok("media", 4.0)
    sh(f"{BIN}/desk-url", "hide")
    krok("koniec", 1.5)


if __name__ == "__main__":
    if not KROKI:
        T0[0] = time.time()
        th = threading.Thread(target=capture, daemon=True)
        th.start()
    try:
        scenariusz()
    finally:
        stop.set()
    if not KROKI:
        th.join(15)
        json.dump({"frames": frames}, open(OUT / "meta.json", "w"))
        print(len(frames), "klatek,", round(frames[-1][0], 1), "s")
        from rolik_common import koduj
        koduj(str(OUT), "pulpit", width=1280)
