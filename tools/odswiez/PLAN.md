# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-21 (dziennik: 3 wpisy; panel agentów przenagrany, 4 kadry: nagłówki bez wersalików, przełącznik motywu, szklany pasek telefonu; głowy bez widocznych zmian)

## Nieaktualne
- Panel: kadry decyzji (panel-decyzje*), modeli (panel-modele*), okładki agenci/panel i filmy agenci.mp4, panel.mp4
  mają jeszcze nagłówki wersalikami sprzed 20.11. Przenagrać tak jak 21.11 panel-agenci: `faketime` 13:35, `DARK`,
  bez pogody (tools/panel-demo/README.md). Grupa „panel” w tabeli odświeżania nie patrzy na gitcloud-core, choć wygląd
  panelu zmienia się głównie w rdzeniu; dopisać rdzeń (static, gate) do źródeł grupy w host/site-refresh.
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): film pulpit.mp4 nagrany ręcznie, przepisu w repo nie ma. Przenagrać dopiero z przepisem
  (profil demo pulpitu, wymyślone pliki, bez prawdziwego ekranu). Od 20.11 pulpit ma okno Ustawień, tryb Skupienie,
  szklane menu i cieńsze ikony.
- Głowy: od 18-19.11 cień pod szczęką i ciepłe podświetlenie od dołu; w kadrach 360 px prawie niewidoczne. Zmiany
  głowy z 20.11 to ruch (wzrok, usta) i szybkość; ciemny ton bez zmian. Przenagrać z następną widoczną zmianą.

## Do pokazania
- Jasny motyw: głowy mają jasne awatary (agenci/<kto>-light.webp, studio na białym). Wpis „ten sam agent w dwóch
  motywach”: kadr jasny obok ciemnego; pilot przez render.py, jeśli symulator umie jasny ton.
- Nowy projekt w katalogu (decyzja właściciela #1312, 13.11): następny projekt z repozytoriów lub Useme, którego
  jeszcze nie ma na stronie; gałąź + zrzuty na danych przykładowych, PL/EN/RU.
- Centrum bezpieczeństwa rdzenia (ocena od 0 do 100, „Napraw”, dziennik tarczy): kadr na danych przykładowych. W
  tools/panel-demo nie ma jeszcze danych tarczy; dopisać je do fake.py jak dla dziennika agentów.
- Tabele rdzenia (szerokość kolumn myszą, numery stron, panel filtrów): przy nagraniu panelu tabela z filtrami.
- Nić sprawy w ruchu: pętla kilku sekund (dane w tools/panel-demo/fake_dec.py, PLANS), screencast jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych.
- Ćwiczenia awarii (serwer z kodu, żywe awarie raz w miesiącu): schemat kroków do strony platformy danych.

## Nie udało się / ograniczenia
- Pilot: okno rozmowy (Sally, Tony) i strona „Dźwięk” są od 18.11 w tools/pilot/scenariusz-glos.txt (warsztat strony).
  Wiersz trybów ze sprawą w toku jeszcze nie występuje w scenariuszu.

## SEO (Marek, obchód 15.11; wszystko poza główną zrobione)
- Title > 70 znaków: główna PL/EN/RU zostaje, to pozycjonowanie właściciela.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
