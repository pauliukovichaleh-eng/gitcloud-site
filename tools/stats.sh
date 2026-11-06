#!/usr/bin/env bash
# Odświeża src/data/stats.json: liczba commitów w repozytoriach ekosystemu GitCloud (gałąź główna, zaokrąglona w dół do setek).
# Liczy tylko własne repozytoria w ~/src; kod pisany u pracodawców i forki (np. whisper.cpp) się nie liczą.
# Uruchamiać lokalnie (CI widzi tylko repozytorium strony), potem commit stats.json.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=${GC_SRC:-$HOME/src}
REPOS=(gitcloud-ai gitcloud-automation gitcloud-core gitcloud-desk gitcloud-remote gitcloud-school gitcloud-site llm-router)
total=0
for r in "${REPOS[@]}"; do
  [ -d "$SRC/$r" ] || { echo "brak $SRC/$r" >&2; continue; }
  n=$(git -C "$SRC/$r" rev-list --count HEAD)
  printf '%6d  %s\n' "$n" "$r"; total=$((total + n))
done
floor=$((total / 100 * 100))
echo "razem $total → $floor+"
node -e '
const fs = require("fs"); const f = "src/data/stats.json"; const s = JSON.parse(fs.readFileSync(f, "utf8"));
s.commits = +process.argv[1]; s.measured = new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Warsaw" }).format(new Date());
fs.writeFileSync(f, JSON.stringify(s, null, 2) + "\n");' "$floor"
