# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-11

## Nieaktualne
- Głowy agentów (agenci/*.webp, glowa-*.mp4, glowy.mp4): nagrane bez ramion. Głowa ma od 10.11 opcję `&withbody=1`
  (ramiona w kadrze), ale to inny kadr i inna kamera niż obecne klipy. Osobne nagranie z ramionami jest zaplanowane
  (12.11, razem z filmami panelu i pilota); nocne odświeżanie go nie dubluje.
- Filmy panelu i pilota (panel.mp4, agenci.mp4, pilot.mp4) i ich plakaty: starszy wygląd niż zdjęcia z 10.11.
  To samo nagranie 12.11.
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”, strona ma spokojną paletę. Przenagrać,
  gdy platforma ISP dostanie ciemny motyw zbliżony do panelu; inaczej zostają.
- Panel: kadry z 10.11 nie pokazują „nici sprawy” przy sesjach Claude (wpis w /zmiany/ z 10.11).
  Demo panelu (tools/panel-demo) nie ma danych przykładowych dla nici; dopisać je do fake.py i zrobić kadr przed/po.
- Pulpit (pulpit-gitcloud): wspólny czat głów i podpis „czym zajęty” nad głową są tylko w tekście dziennika, bez kadru.

## Do pokazania
- Nić sprawy: krótki kadr (WebP) albo pętla kilku sekund: pasek idzie, zatrzymuje się, kończy na zielono.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych (bez prawdziwych rozmów).
- Opis projektu panelu: po kadrze nici dopisać jedno zdanie o nici sprawy (projects.json + i18n).
- Głowy z ramionami: po nagraniu 12.11 wpis wizualny przed/po w /zmiany/, jeśli nie zrobi go samo nagranie.

## Nie udało się / ograniczenia
- Przepis filmów głów (kadrowanie 960×474 i 1280×632 z klatek clip.py) jest poza repo; przenieść do
  tools/glowy/ razem z nagraniem z ramionami.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, CI dzień/noc)
  na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
