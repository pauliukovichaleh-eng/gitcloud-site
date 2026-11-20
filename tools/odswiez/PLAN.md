# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-20 (dziennik: 3 wpisy; głowy przenagrane w ciemnym tonie, różnica w 360 px niewidoczna, zostały stare; pilot i panel bez zmian w ciemnym motywie)

## Nieaktualne
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): film pulpit.mp4 nagrany ręcznie, przepisu w repo nie ma. Przenagrać dopiero z przepisem
  (profil demo pulpitu, wymyślone pliki, bez prawdziwego ekranu). Od 14.11 pulpit ma szklane menu nad stroną.
- Głowy: od 18-19.11 cień pod szczęką i ciepłe podświetlenie od dołu; w kadrach 360 px prawie niewidoczne (19 i 20.11
  przenagrane, zostały stare). Przenagrać razem z następną widoczną zmianą. clip.py wymusza teraz &tone=dark.

## Do pokazania
- Jasny motyw (19.11): głowy mają jasne skórki (porcelanowa obudowa, srebrne włosy Sally), pilot paletę jasnego tonu.
  Wpis wizualny „ten sam agent w dwóch motywach”: clip.py z &tone=light, kadr obok ciemnego; pilot przez render.py,
  jeśli symulator umie jasny ton.
- Nowy projekt w katalogu (decyzja właściciela #1312, 13.11): następny projekt z repozytoriów lub Useme, którego
  jeszcze nie ma na stronie; gałąź + zrzuty na danych przykładowych, PL/EN/RU.
- Centrum bezpieczeństwa rdzenia (ocena od 0 do 100, „Napraw”, dziennik tarczy): kadr na danych przykładowych. W
  tools/panel-demo nie ma jeszcze danych tarczy; dopisać je do fake.py jak dla dziennika agentów.
- Tabele rdzenia (szerokość kolumn myszą, numery stron, panel filtrów) i jedna skala przycisków: przy następnym
  nagraniu panelu pokazać tabelę z panelem filtrów.
- Nić sprawy w ruchu: pętla kilku sekund (dane w tools/panel-demo/fake_dec.py, PLANS), screencast jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych.
- Ćwiczenia awarii (serwer z kodu w zagnieżdżonej maszynie): schemat kroków do strony platformy danych, od zera.

## Nie udało się / ograniczenia
- Pilot: okno rozmowy (Sally, Tony) i strona „Dźwięk” są od 18.11 w tools/pilot/scenariusz-glos.txt (warsztat strony).
  Wiersz trybów ze sprawą w toku jeszcze nie występuje w scenariuszu.

## SEO (Marek, obchód 15.11; zrobione: EN/RU platforma-dzialu-it, EN baza-b2b-nl-be, RU dyzurny; /cv/ od 18.11 noindex i poza mapą)
- Title > 70 znaków: główna PL/EN/RU (od 18.11: 80/85/78) zostaje, to pozycjonowanie właściciela.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
