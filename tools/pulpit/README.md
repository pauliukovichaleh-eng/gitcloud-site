# Film i zrzuty „Pulpit GitCloud” na danych przykładowych

Pulpit (prywatne repozytorium gitcloud-desk, zainstalowany w `~/.config/gitcloud-desk`) uruchomiony w osobnej, niewidocznej
sesji sway na karcie graficznej, w wymyślonym katalogu domowym. Nic z prawdziwej sesji nie trafia do kadru: panel po lewej
to demo-panel z `tools/panel-demo`, pasek, powiadomienia i odtwarzacz mają własną magistralę D-Bus, konsola — własny serwer
kart i własny tmux, pliki i zdjęcia są wymyślone.

    tools/pulpit/przygotuj.sh                       # katalog domowy ~/.cache/gitcloud/pulpit-demo/home (FILM=… — film przykładowy)
    tools/pulpit/sesja.sh start                     # demo-panel :18932, sway headless 1920×1080, zmienne w <katalog>/env
    python3 tools/pulpit/scenariusz.py KAT --kroki  # strojenie: zrzut PNG po każdym kroku
    python3 tools/pulpit/scenariusz.py KAT          # film → public/img/projekty/pulpit.mp4 i pulpit-wideo.jpg
    tools/pulpit/sesja.sh stop

`przygotuj.sh` kopiuje pulpit bez tokenów, profili przeglądarki i kopii zapasowych, przestawia pasek i okno strony na
demo-panel (`/lang/pl`), usuwa z konfiguracji sway wszystko, co dotyka prawdziwej sesji (środowisko systemd i D-Bus
użytkownika, klucze, bezczynność, ekrany), dokłada przykładowe foldery, zdjęcia (obrazy z `public/img/projekty`), film
i małe repozytorium. Pogoda: deszcz (`sky.json`), godzina: wieczór — `sesja.sh` przesuwa strefę czasową.

Polskie napisy: interfejs pulpitu jest po rosyjsku, więc `pl.js` (ze słownikiem `slownik.json`: `teksty` — całe napisy,
`wzorce` — wyrażenia regularne) podmienia teksty i podpowiedzi w każdej stronie aplikacji. Widoczny tekst z cyrylicą,
którego nie ma w słowniku, `sesja.sh` zbiera do `<katalog>/braki.txt` — z tej listy uzupełnia się słownik.

Scenariusz: pulpit z miastem w deszczu i podłogą w rytm muzyki (`gc-floor --demo`: rytm syntetyczny, bez
prawdziwego odtwarzacza), powiadomienie GitCloud z paska, Pliki w ramce GitCloud (przeciągnięcie za nagłówek, rozwinięcie na
cały pulpit i powrót), zdjęcie w GitCloud Foto, szybkie wyszukiwanie, film w GitCloud Media. Kursor i kliknięcia
`swaymsg seat seat0 cursor …`. Klatki `grim -c` (z kursorem) jako PPM 1920×1080 (ok. 18/s), czasy w `meta.json`, kodowanie
`koduj()` z `tools/panel-demo/rolik_common.py` (H.264, bez dźwięku).

Przed publikacją: `~/job-hunter/.venv/bin/python -I tools/odswiez/ocr.py public/img/projekty/pulpit*` (słowa zakazane,
prywatne adresy IP) i przegląd klatek pod kątem cyrylicy. Film nie idzie do git: `tools/media.sh push public/img/projekty/pulpit.mp4`.
