# Plan prowadzenia strony (aktualizowany co noc)

Ostatnia noc: 2026-11-25 (dziennik: 3 wpisy; panel: kadry modeli i decyzji przenagrane; pilot: 5 ekranów i film z
nowym tłem-schematem; głowy bez widocznych zmian; Tarcza: krótszy title PL)

## Nieaktualne
- Panel: okładki agenci/panel i filmy agenci.mp4, panel.mp4 mają jeszcze nagłówki wersalikami sprzed 20.11 i stare
  etykiety stanu słowami (od 24.11 ikony stanu rdzenia). Przenagrać jak 25.11 kadry modeli: `faketime '<data> 13:35'`,
  `DARK`, bez pogody (tools/panel-demo/README.md). Grupa „panel” w tabeli odświeżania nie patrzy na gitcloud-core,
  choć wygląd panelu zmienia się głównie w rdzeniu; dopisać rdzeń (static, gate) do źródeł grupy w host/site-refresh.
- Tarcza (/bezopasnost): od 22-24.11 jedna lista „Zdarzenia bezpieczeństwa” zamiast czterech dzienników i ikony stanu.
  Kadry tarcza-* są starsze. Przed nagraniem sprawdzić, czy fake_sec.py pokrywa nowe sekcje (potwierdzenia twarzą,
  klucz Face ID) danymi przykładowymi; sekcja potwierdzeń dotyka płatności, więc ukryć ją jak ochronę mieszkania.
- Konsola ISP (public/img/demo): zrzuty z 05.11 w niebieskim motywie „Kolor”. Przenagrać, gdy platforma ISP dostanie
  ciemny motyw zbliżony do panelu; inaczej zostają.
- Pulpit (pulpit-gitcloud): film pulpit.mp4 nagrany ręcznie, przepisu w repo nie ma. Od 24.11 pulpit ma okno „Hasła”,
  własne okna wyboru pliku i druku, nową kartę przeglądarki w stylu GitCloud. Przenagrać dopiero z przepisem
  (profil demo pulpitu, wymyślone pliki, bez prawdziwego ekranu).
- Głowy: podświetlenie od dołu mocniejsze od 23.11 (0,9 → 1,6), sprawdzone parą kadrów: w 360 px nadal prawie
  niewidoczne, więc bez przenagrania. Przenagrać z następną widoczną zmianą (dark i TONE=light).

## Do pokazania
- Jasny motyw: wpis „ten sam agent w dwóch motywach”: głowa jasna obok ciemnej; pilot w jasnym motywie ma teraz
  schemat na jasnym papierze (render.py: sprawdzić, czy symulator przełącza ton).
- Pilot: twarze Tony i Buzz w oknie rozmowy (3.227.2) zamiast starych; scenariusz-glos.txt pokazuje Tony; dodać kadr Buzza.
- Nowy projekt w katalogu (decyzja właściciela #1312, 13.11): następny projekt z repozytoriów, którego jeszcze nie ma
  na stronie; gałąź + zrzuty na danych przykładowych, PL/EN/RU. Kandydat: GitCloud OS (instalator, kreator kont).
- Wyszukiwanie Ctrl+K po danych (decyzje, katalog) i okna Issue/PR GitHub w panelu: kadr na danych przykładowych.
- Tabele rdzenia (szerokość kolumn myszą, numery stron, panel filtrów): przy nagraniu panelu tabela z filtrami.
- Nić sprawy w ruchu: pętla kilku sekund (dane w tools/panel-demo/fake_dec.py, PLANS), screencast jak rolik.py.
- Czat głów na pulpicie: kadr z trzema awatarami na danych przykładowych.

## Nie udało się / ograniczenia
- Pilot: wiersz trybów ze sprawą w toku jeszcze nie występuje w scenariuszu.

## SEO (Marek, obchód 22.11)
- Title > 70 znaków: główna PL/EN/RU zostaje, to pozycjonowanie właściciela. Tarcza PL skrócona 25.11 (69 znaków).

## Pomysły
- Krótki film „noc w GitCloud”: co robią zadania nocne (kopie, przegląd kodu, łatki zależności, dokumentacja) na
  danych przykładowych.
- Strona Dyżurny admin: przykład grupowania błędów w logach (ślady, serie) jako schemat, bez prawdziwych logów.
