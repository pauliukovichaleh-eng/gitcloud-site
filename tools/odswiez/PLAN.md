# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-17 (dziennik: 2 wpisy techniczne; kadry pilota, głów i panelu bez zmian; SEO: 2 tytuły)

## Nieaktualne
- Film panel.mp4 (12.11): zakładka „Modele” ma już podzakładki rdzenia (zużycie, przebiegi, wynik, limity i trasy),
  a twarze agentów są nowe. Przenagrać `rolik_panel.py` (panel uruchomić od nowa przed nagraniem).
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): film pulpit.mp4 nagrany ręcznie, przepisu w repo nie ma. Przenagrać dopiero z przepisem
  (profil demo pulpitu, wymyślone pliki, bez prawdziwego ekranu). Od 14.11 pulpit ma szklane menu nad stroną.

## Do pokazania
- Pilot 3.218.0: okno rozmowy z twarzą agenta w sześciokącie i 24 segmentami głosu. W scenariuszu render.py nie ma
  tego ekranu; dopisać kadr (wiadomość głosowa z danymi przykładowymi) i sprawdzić, czy symulator ma zasoby twarzy.
- Nowy projekt w katalogu (decyzja właściciela #1312, 13.11): następny projekt z repozytoriów lub Useme, którego
  jeszcze nie ma na stronie; gałąź + zrzuty na danych przykładowych, PL/EN/RU.
- Centrum bezpieczeństwa rdzenia (ocena od 0 do 100, „Napraw”, dziennik tarczy): kadr na danych przykładowych. W
  tools/panel-demo nie ma jeszcze danych tarczy; dopisać je do fake.py jak dla dziennika agentów.
- Nić sprawy w ruchu: pętla kilku sekund (dane w tools/panel-demo/fake_dec.py, PLANS), screencast jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych.
- Szyna zdarzeń rdzenia: schemat „zdarzenie → zadanie” zamiast timerów (do strony rdzenia), rysowany od zera.

## Nie udało się / ograniczenia
- Głowy 17.11: zmiany tylko w trybie muzyki i w napisach (wygląd w klipach ten sam), bez przenagrania.
- Pilot 17.11: render.py daje kadry identyczne co do piksela; nowa strona „Dźwięk” (głośności) i wiersz trybów
  ze sprawą w toku nie występują w scenariuszu. Do dopisania razem z oknem rozmowy (dane przykładowe, PL).
- Panel 17.11: zmiany w sekcjach prywatnych i w nazwach serwerów (przycisk mostu w kadrach ukryty), bez przenagrania.

## SEO (Marek, obchód 15.11)
- Title > 70 znaków: główna PL/EN/RU (72/71/74) zostaje, to pozycjonowanie właściciela.
- Title > 70: EN i RU platforma-dzialu-it (71/71); skrócić o kilka znaków.
- Description /cv/ PL i EN (197/202): składa się z roli i pierwszego akapitu bio; potrzebne osobne krótkie pole opisu.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
