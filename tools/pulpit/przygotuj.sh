#!/usr/bin/env bash
# Wymyślony katalog domowy do nagrania pulpitu GitCloud (README.md): kopia zainstalowanego pulpitu bez sekretów i profili,
# konfiguracja przestawiona na demo-panel i własne porty, polskie napisy (pl.js), przykładowe foldery, zdjęcia, film i repozytorium.
#   tools/pulpit/przygotuj.sh [KATALOG]      domyślnie ~/.cache/gitcloud/pulpit-demo
set -euo pipefail
T=$(cd "$(dirname "$0")" && pwd); S=$(cd "$T/../.." && pwd)
D=${1:-$HOME/.cache/gitcloud/pulpit-demo}; H=$D/home; SRC=$HOME/.config/gitcloud-desk
PANEL=${PANEL:-http://127.0.0.1:18932}
[ -d "$SRC" ] || { echo "brak $SRC (pulpit nie zainstalowany)" >&2; exit 1; }
rm -rf "$H"; mkdir -p "$H/.config" "$D"
# kopia pulpitu: bez tokenów, portów, profili przeglądarki, kopii zapasowych i zmiennych domu
rsync -a --exclude 'kiosk-profile' --exclude 'token' --exclude 'port' --exclude '*.bak*' --exclude 'home-vars.yml' \
  --exclude '__pycache__' "$SRC/" "$H/.config/gitcloud-desk/"
C=$H/.config/gitcloud-desk
python3 - "$C" "$PANEL" <<'PY'
import json, re, sys
c, panel = sys.argv[1], sys.argv[2]
b = json.load(open(f"{c}/bar.json"))
b.update(site_url=panel + "/", bell_url=panel + "/bell", site_nav_url=panel + "/", side_url=panel + "/stol",
         badges_cmd="", heads_url="", head_h=0, audio_modes=[], audio_toggles=[], audio_mode_file="", chats_port=18784,
         sounds=False, net_if="lo", zanaves=False)
json.dump(b, open(f"{c}/bar.json", "w"), ensure_ascii=False)
s = json.load(open(f"{c}/shell/config.json"))
s.update(url=panel + "/agenty", domain="127.0.0.1", auth_hosts=[])
json.dump(s, open(f"{c}/shell/config.json", "w"), ensure_ascii=False)
# sway: bez usług prawdziwej sesji (środowisko systemd i D-Bus użytkownika, klucze, bezczynność, ekrany, agenty)
skip = re.compile(r"import-environment|dbus-update-activation|gnome-keyring|tmux -L claude|lxpolkit|easyeffects|desk-run swayidle"
                  r"|desk-displays|desk-music-watch|kbd-watch|max_render_time|settings\.sway|xkb_layout|lock-session|^\s*bindswitch")
out = ["output * resolution 1920x1080 scale 1\n"] + [l for l in open(f"{c}/sway.conf") if not skip.search(l)]
out.append("exec sh -c 'echo \"$DBUS_SESSION_BUS_ADDRESS\" > \"$XDG_RUNTIME_DIR/pd-bus\"'   # magistrala sesji dla scenariusza\n")
open(f"{c}/sway.conf", "w").writelines(out)
PY
# polskie napisy: pl.js (słownik slownik.json wklejony w skrypt) w każdej stronie aplikacji pulpitu
python3 - "$T" "$D/pl.js" <<'PY'
import json, sys
t, out = sys.argv[1], sys.argv[2]
sl = json.load(open(f"{t}/slownik.json"))
js = open(f"{t}/pl.js").read().replace("__SL__", json.dumps(sl["teksty"], ensure_ascii=False)).replace("__RX__", json.dumps(sl["wzorce"], ensure_ascii=False))
open(out, "w").write(js)
PY
for f in "$C"/{bar,files,photos,media,console,player,settings}/web/*.html; do
  [ -f "$f" ] || continue; cp "$D/pl.js" "$(dirname "$f")/pl.js"
  python3 - "$f" <<'PY'
import re, sys
f = sys.argv[1]; h = open(f).read()
m = re.search(r'(?:href|src)="([^"]*?)tokens\.css', h)          # ten sam katalog co tokens.css strony
src = (m.group(1) if m else "") + "pl.js"
if "pl.js" not in h:
    h = h.replace("</head>", f'<script src="{src}"></script></head>', 1) if "</head>" in h else f'<script src="{src}"></script>' + h
open(f, "w").write(h)
PY
done
# tytuły okien GTK (nie strony): po polsku
sed -i 's/title="GitCloud Фото"/title="GitCloud Zdjęcia"/' "$C/bin/gitcloud-photos"
sed -i 's/else "GitCloud Медиа")/else "GitCloud Media")/' "$C/bin/gitcloud-media"
# podłoga: rytm syntetyczny (--demo, bez prawdziwego agenta muzyki), alarmy z demo-panelu
sed -i 's#bin/gc-floor >>#bin/gc-floor --demo --state-port 18932 >>#' "$C/bin/desk-run"
# desk-run nie uruchamia paska, podłogi i przyklejania, gdy działają w prawdziwej sesji (pgrep widzi wszystkie procesy) — w demo bez tej blokady
sed -i "/if pgrep .*then sleep 5; continue; fi/d" "$C/bin/desk-run"
# kursor GitCloud i fonty użytkownika (dowiązania: bez kopii)
mkdir -p "$H/.local/share/icons" "$H/.local/share"
[ -d "$HOME/.local/share/icons/GitCloud" ] && ln -s "$HOME/.local/share/icons/GitCloud" "$H/.local/share/icons/GitCloud"
[ -d "$HOME/.local/share/fonts" ] && ln -s "$HOME/.local/share/fonts" "$H/.local/share/fonts"
# dane przykładowe
cd "$H"
mkdir -p Dokumenty Obrazy Pobrane Muzyka Wideo Projekty/katalog-www/{public,tools} .local/state/gitcloud .config
cat > .config/user-dirs.dirs <<'X'
XDG_DOCUMENTS_DIR="$HOME/Dokumenty"
XDG_DOWNLOAD_DIR="$HOME/Pobrane"
XDG_PICTURES_DIR="$HOME/Obrazy"
XDG_MUSIC_DIR="$HOME/Muzyka"
XDG_VIDEOS_DIR="$HOME/Wideo"
X
P=$S/public/img/projekty
for i in ekran-scena-1 ekran-scena-2 ekran-okladka glowy platforma-okladka panel-okladka; do
  f=$(ls "$P/$i".* 2>/dev/null | head -1); [ -n "$f" ] && cp "$f" "Obrazy/"
done
F=${FILM:-$P/glowy.mp4}; [ -f "$F" ] && cp "$F" Wideo/awatary.mp4   # film przykładowy: FILM=… albo glowy.mp4 po media.sh fetch
printf 'Oferta — sklep demo\n' > Dokumenty/oferta.md; printf 'Plan wdrożenia\n' > Dokumenty/plan-wdrozenia.md
printf 'a,b\n1,2\n' > Pobrane/raport.csv
(cd Projekty/katalog-www && git init -q -b main && git config user.name demo && git config user.email demo@example.com &&
  printf '# Katalog projektów\n' > README.md && printf '{"projekty": []}\n' > projects.json && printf 'print("ok")\n' > build.py &&
  git add -A && git commit -qm "Katalog projektów: dane w projects.json" &&
  printf '<h1>Sklep demo</h1>\n' > public/index.html && git add -A && git commit -qm "Strona główna sklepu demo" &&
  printf 'sitemap\n' > public/sitemap.txt && git add -A && git commit -qm "Mapa strony po publikacji")
printf "PS1='demo:\\w\\$ '\n" > .bashrc; cp .bashrc .bash_profile   # znak zachęty bez nazwy prawdziwego komputera
# pogoda i wydarzenia pulpitu: deszcz, wieczór (TZ w sesja.sh), jedno powiadomienie
now=$(date +%s)
printf '{"at": %s, "rain": 2.0, "snow": 0.0, "fog": 0, "cloud": 90, "sunrise": 420, "sunset": 960}\n' "$now" > .local/state/gitcloud/sky.json
: > .local/state/gitcloud/events.jsonl
echo "gotowe: $H"
