#!/usr/bin/env bash
# Filmy strony (public/img/projekty/*.mp4) trzymane w wydaniu GitHub „media”, nie w git (decyzja #752, 07.11.2026):
# każde przenagranie zostawałoby w historii na zawsze. Workflow deploy/lighthouse pobiera je przed buildem.
#   tools/media.sh fetch            pobierz wszystkie filmy do public/img/projekty (lokalny build)
#   tools/media.sh push PLIK.mp4…   wgraj/podmień w wydaniu (stara wersja: tools/media.sh backup KATALOG przed podmianą)
#   tools/media.sh backup KATALOG   pobierz obecne filmy z wydania do KATALOG (do cofnięcia nocy)
set -euo pipefail
R=pauliukovichaleh-eng/gitcloud-site
cd "$(dirname "$0")/.."
case "${1:-}" in
  fetch)  gh release download media -R $R -p '*.mp4' -D public/img/projekty --clobber ;;
  push)   shift; gh release upload media -R $R --clobber "$@" ;;
  backup) mkdir -p "$2"; gh release download media -R $R -p '*.mp4' -D "$2" --clobber ;;
  *) sed -n 2,7p "$0"; exit 2 ;;
esac
