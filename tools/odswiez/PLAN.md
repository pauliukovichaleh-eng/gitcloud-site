# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-18 (dziennik: 3 wpisy; przenagrana głowa Marka; panel bez zmian; SEO: 2 tytuły; stos platformy danych)

## Nieaktualne
- Film panel.mp4 (12.11): zakładka „Modele” ma już podzakładki rdzenia (zużycie, przebiegi, wynik, limity i trasy),
  a twarze agentów są nowe. Przenagrać `rolik_panel.py` (panel uruchomić od nowa przed nagraniem).
- Panel od 17.11: na serwerze Sally agent domowy to Buzz (z twarzą Marka do czasu własnej głowy), Mark zostaje
  w innej roli. Kadry panel-agenci, panel-decyzje, agenci.mp4 pokazują jeszcze Marka. Przenagrać i opisać
  Buzza w sekcji „Agenci”. Od 18.11 Buzz ma własną głowę (head.js: własna twarz, bez monokla i mikrofonu, neon
  liliowy; serwer głów Sally rysuje go sam, z pliku: `?who=mark&buzz=1`). Do zrobienia najbliższej nocy: nagrać głowy
  z Buzzem (clip.py z `buzz=1`), w tekstach strony (i18n „Agenci AI”, Home.astro agentMeta, projects*.json alt)
  Mark → Buzz (rola: spokojny badacz, rzadko mówi, 1–2 pomysły z ceną i zyskiem). Wpisy dziennika o Marku zostają.
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
- Pilot 17.11: render.py daje kadry identyczne co do piksela; nowa strona „Dźwięk” (głośności) i wiersz trybów
  ze sprawą w toku nie występują w scenariuszu. Do dopisania razem z oknem rozmowy (dane przykładowe, PL).
- Panel 18.11: Buzz zamiast Marka i kafel zadań kontenera zamiast Cronicle; bez przenagrania (patrz „Nieaktualne”).
- Głowy 18.11: Tony i Sally po ponownym renderze różnią się tylko odcieniem skóry, zostały stare pliki; trójka
  glowy.mp4 i Mark nowe.

## SEO (Marek, obchód 15.11; zrobione: EN/RU platforma-dzialu-it 18.11)
- Title > 70 znaków: główna PL/EN/RU (72/71/74) zostaje, to pozycjonowanie właściciela.
- Description /cv/ PL i EN (197/202): składa się z roli i pierwszego akapitu bio; potrzebne osobne krótkie pole opisu.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
