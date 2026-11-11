# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-11 (druga runda: kadry decyzji panelu z nicią sprawy)

## Nieaktualne
- Panel: zrzuty agentów (panel-agenci*, panel-tony, panel-sally) i modeli (panel-modele*) są jeszcze w neonowej palecie;
  panel ma od 11.11 spokojniejszą (kadry decyzji już nowe). Przenagrać `final.py` (bez trybu i `modele`), jedna noc.
- Głowy agentów (agenci/*.webp, glowa-*.mp4, glowy.mp4): nagrane bez ramion i bez nowego połysku włosów przy ruchu
  (11.11, widać tylko w ruchu). Głowa ma `&withbody=1`; osobne nagranie z ramionami zaplanowane na 12.11 (razem
  z filmami panelu i pilota), nocne odświeżanie go nie dubluje.
- Filmy panelu i pilota (panel.mp4, agenci.mp4, pilot.mp4) i plakaty: starszy wygląd. To samo nagranie 12.11.
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): wspólny czat głów i podpis „czym zajęty” nad głową są tylko w tekście dziennika, bez kadru.

## Do pokazania
- Nić sprawy w ruchu: pętla kilku sekund (pasek idzie, zatrzymuje się, kończy na zielono); dane są już w
  tools/panel-demo/fake_dec.py (PLANS), wystarczy nagranie screencastem jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych (bez prawdziwych rozmów).
- Głowy z ramionami: po nagraniu 12.11 wpis wizualny przed/po w /zmiany/, jeśli nie zrobi go samo nagranie.

## Nie udało się / ograniczenia
- Przepis filmów głów (kadrowanie 960×474 i 1280×632 z klatek clip.py) jest poza repo; przenieść do
  tools/glowy/ razem z nagraniem z ramionami.
- Okładka panelu (panel-okladka.webp) to dziś kadr strony modeli, a tools/okladki/panel.html składa starszą okładkę
  z kart decyzji; ustalić, który przepis jest aktualny, zanim okładka będzie przenagrywana.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
