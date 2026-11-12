#!/usr/bin/env bash
# Pulpit GitCloud w osobnej, niewidocznej sesji sway (headless, karta graficzna) na wymyślonym katalogu domowym (przygotuj.sh).
#   tools/pulpit/sesja.sh start [KATALOG]   demo-panel :18932, zbieracz nieprzetłumaczonych napisów :18799, sway; wypisuje zmienne
#   tools/pulpit/sesja.sh stop  [KATALOG]   zatrzymuje wszystko po zapisanych PID-ach (nie po tekście polecenia)
# Własna magistrala D-Bus (dbus-run-session) i własny XDG_RUNTIME_DIR: pasek, odtwarzacz i powiadomienia nie widzą prawdziwej sesji.
# Godzina: strefa czasowa przesunięta tak, żeby na pulpicie był wieczór (miasto z oknami), pogoda — deszcz (sky.json).
set -euo pipefail
T=$(cd "$(dirname "$0")" && pwd); S=$(cd "$T/../.." && pwd)
cmd=${1:-}; D=${2:-$HOME/.cache/gitcloud/pulpit-demo}; H=$D/home; R=/tmp/pd-$UID; PIDS=$D/pids
case $cmd in
start)
  [ -d "$H" ] || { echo "najpierw przygotuj.sh" >&2; exit 1; }
  mkdir -p "$R" && chmod 700 "$R"; : > "$PIDS"; : > "$D/braki.txt"
  ( cd ~/src/gitcloud-ai && DEMO_LANG=pl DEMO_INIT=1 PORT=18932 exec nice -n 19 .venv/bin/python "$S/tools/panel-demo/run.py" ) >"$D/panel.log" 2>&1 & echo $! >> "$PIDS"
  python3 - "$D/braki.txt" >"$D/braki.log" 2>&1 <<'PY' & echo $! >> "$PIDS"
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
out = sys.argv[1]
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        t = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode(errors="replace")
        with open(out, "a") as f: f.write(t.replace("\n", " ") + "\n")
        self.send_response(204); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
    def log_message(self, *a): pass
HTTPServer(("127.0.0.1", 18799), H).serve_forever()
PY
  for i in $(seq 60); do curl -s -o /dev/null -m 2 http://127.0.0.1:18932/ && break; sleep 1; done
  # wieczór: przesunięcie strefy tak, żeby lokalnie była ok. 20:30
  utc=$(( 10#$(date -u +%H) * 60 + 10#$(date -u +%M) )); off=$(( (20 * 60 + 30 - utc + 1440 * 2) % 1440 )); off=$(( (off + 30) / 60 )); [ $off -gt 12 ] && off=$((off - 24))
  tz="Etc/GMT$( [ $off -le 0 ] && echo + || true)$((-off))"   # Etc/GMT+N = UTC−N; strefę rozumie też WebKit (ICU), zapis POSIX nie
  sed -i "s/\"at\": [0-9]*/\"at\": $(date +%s)/" "$H/.local/state/gitcloud/sky.json"
  env -i HOME="$H" USER="$USER" LOGNAME="$USER" PATH=/usr/local/bin:/usr/bin:/bin SHELL=/bin/bash LANG=pl_PL.UTF-8 LC_ALL=C.UTF-8 \
    TZ="$tz" XDG_RUNTIME_DIR="$R" XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=sway \
    WLR_BACKENDS=headless WLR_HEADLESS_OUTPUTS=1 WLR_RENDERER=gles2 WLR_RENDER_DRM_DEVICE=/dev/dri/renderD128 WLR_LIBINPUT_NO_DEVICES=1 \
    GC_CONSOLE_PORT=18779 GC_CONSOLE_TMUX=pulpit-demo GC_CONSOLE_START=shell GC_FILES_PORT=18781 NO_AT_BRIDGE=1 GTK_A11Y=none \
    setsid nice -n 19 dbus-run-session -- sway -c "$H/.config/gitcloud-desk/sway.conf" >"$D/sway.log" 2>&1 < /dev/null & echo $! >> "$PIDS"
  for i in $(seq 40); do s=$(ls "$R"/sway-ipc.*.sock 2>/dev/null | head -1 || true); [ -n "$s" ] && break; sleep 0.5; done
  [ -n "${s:-}" ] || { echo "sway nie wstał, zob. $D/sway.log" >&2; exit 1; }
  printf 'export SWAYSOCK=%s WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=%s HOME_DEMO=%s\n' "$s" "$R" "$H" | tee "$D/env" ;;
stop)
  [ -f "$PIDS" ] && while read -r p; do kill -- -"$p" 2>/dev/null || kill "$p" 2>/dev/null || true; done < "$PIDS"
  for e in /proc/[0-9]*/environ; do   # resztki sesji (np. serwer kart konsoli) — po katalogu domowym demo, nie po tekście polecenia
    { tr '\0' '\n' < "$e"; } 2>/dev/null | grep -qx "HOME=$H" && kill "$(basename "$(dirname "$e")")" 2>/dev/null || true
  done
  for port in 18932 18799; do   # demo-panel i zbieracz z wcześniejszego startu (plik PID nadpisany)
    for p in $(ss -ltnpH "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2); do kill "$p" 2>/dev/null || true; done
  done
  s=$(ls "$R"/sway-ipc.*.sock 2>/dev/null | head -1 || true); [ -n "$s" ] && SWAYSOCK=$s swaymsg -q exit 2>/dev/null || true
  tmux -L pulpit-demo kill-server 2>/dev/null || true; rm -f "$PIDS"; echo zatrzymane ;;
*) sed -n 2,6p "$0"; exit 2 ;;
esac
