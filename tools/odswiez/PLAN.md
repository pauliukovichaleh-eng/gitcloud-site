# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-14 (panel: Agenci i Modele z modułów rdzenia, nowe twarze; dziennik: 3 wpisy)

## Nieaktualne
- Film panel.mp4 (12.11): zakładka „Modele” ma już podzakładki rdzenia (zużycie, przebiegi, wynik, limity i trasy),
  a twarze agentów są nowe. Przenagrać `rolik_panel.py` (panel uruchomić od nowa przed nagraniem).
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): film pulpit.mp4 nagrany ręcznie, przepisu w repo nie ma. Przenagrać dopiero z przepisem
  (profil demo pulpitu, wymyślone pliki, bez prawdziwego ekranu).

## Do pokazania
- Centrum bezpieczeństwa rdzenia (ocena od 0 do 100, „Napraw”, dziennik tarczy): kadr na danych przykładowych. W
  tools/panel-demo nie ma jeszcze danych tarczy; dopisać je do fake.py jak dla dziennika agentów.
- Nić sprawy w ruchu: pętla kilku sekund (dane w tools/panel-demo/fake_dec.py, PLANS), screencast jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych.

## Nie udało się / ograniczenia
- Głowy: po kadrach z 13.11 doszła tylko średnia warstwa porów (działa w małym oknie, w kadrze 360 px niewidoczna),
  więc bez przenagrania. Pilot: zniknęła lista rankingu, której na stronie nie było; bez przenagrania.

## SEO (Marek, obchód 12.11)
- Title > 70 znaków: główna PL/EN/RU (72/71/74) zostaje, to pozycjonowanie właściciela.
- Title > 70: pulpit-gitcloud PL i RU (71/72), EN baza-b2b-nl-be (72), RU dyzurny (74); skrócić o kilka znaków.
- Description /cv/ PL i EN (197/202): składa się z roli i pierwszego akapitu bio; potrzebne osobne krótkie pole opisu.

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, dokumentacja, przenoszenie wspólnego
  kodu do rdzenia, CI dzień/noc) na danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
