# Zrzuty panelu agentów na danych przykładowych

Panel (prywatne repozytorium gitcloud-ai) uruchomiony bez bazy i bez sieci: `run.py` odcina połączenia wychodzące
i podprocesy, zapytania SQL obsługuje `fake.py` (wymyślony dziennik spraw agentów), resztę zwraca pustą.

    cd ~/src/gitcloud-ai && PORT=18932 .venv/bin/python <repo>/tools/panel-demo/run.py &
    python final.py http://my.gitcloud.pl:18932 <katalog>    # Playwright, Chrome z MAP my.gitcloud.pl 127.0.0.1

`final.py` tłumaczy kilka brakujących napisów na polski i sprawdza, czy w kadrze nie ma cyrylicy. Wspólne dla zrzutów
i filmów jest w `rolik_common.py`: zamiany napisów `PL`, `HIDE` (bez „Dom (tylko odczyt)”, przycisku mostu i paska
finansów), kontrola cyrylicy `CYR`, kodowanie filmu `koduj`. Warsztaty (`workshop.py`) czytają prawdziwy stan z dysku,
więc `fake.py` je wyłącza.
Obrazy: PNG → WebP (jakość 82) do public/img/projekty/panel-*.webp.

Strona modeli (`/ai-router`): `fake_llm.py` generuje wymyślone wywołania LLM z 30 dni (wymyślone aplikacje agentów,
publiczne nazwy modeli, kwoty i salda przykładowe), wynik jakości modeli i limity; podmienia status bramki LLM,
salda i nocny przegląd kodu. Zrzuty: `python final.py http://my.gitcloud.pl:18932 <katalog> modele`.

Karty decyzji (pulpit Claude na stronie głównej panelu): `fake_dec.py` daje wymyślone pytania agentów do właściciela
z wariantami, dziennik decyzji z wynikami, dwie sesje Claude i limity. Zrzuty samego widżetu:
`python final.py http://my.gitcloud.pl:18932 <katalog> decyzje` (komputer, komputer z rozwiniętymi szczegółami i dziennikiem, telefon).

Okładka karty „Panel operacyjny” (16:9): wycinek 1280×720 ze zrzutu `/ai-router` w 2x (`DSF=2 python final.py … modele`),
od punktu (190, 192): saldo poniżej etykiety kategorii karty także na telefonie (karta 2:1 ucina górę). WebP (jakość 82) do `public/img/projekty/panel-okladka.webp`.

Okładka karty „Agenci AI” (16:9): wycinek 1280×720 ze zrzutu `/agenty` w 2x (`DSF=2 python final.py … <katalog>`),
WebP (jakość 82) do `public/img/projekty/agenci-okladka.webp`.

Film „Agenci AI” (`/img/projekty/agenci.mp4`, 1280×720, ok. 25 s): `python rolik.py <katalog>` nagrywa przejście
po panelu (przegląd /agenty, szczegóły sprawy, karty Tony, Sally, Mark) przez CDP screencast (JPEG 92) z narysowanym
kursorem; tłumaczy opisy postaci na polski, ukrywa listę harmonogramu i sprawdza cyrylicę w kadrze w każdym punkcie.
Na końcu `koduj()`: klatki → ffconcat z czasami → H.264 (`-preset veryslow -crf 28 -tune stillimage`) prosto do
`public/img/projekty/agenci.mp4`, plakat `agenci-wideo.jpg` = klatka z 2. sekundy.

Film „Panel operacyjny” (`/img/projekty/panel.mp4`, 1280×720, ok. 33 s): przed nagraniem uruchomić panel od nowa
(odpowiedź zmienia dane `fake_dec.py` do restartu), potem `python rolik_panel.py <katalog>`. Scenariusz: pulpit Claude
na stronie głównej → szczegóły pytania → odpowiedź jednym kliknięciem (chwila na cofnięcie, potem „w trakcie”, karta
przechodzi do dziennika z wymyślonym wynikiem) → dziennik decyzji → zakładka „Modele”, rozwinięty wynik modelu.
Pasek finansów u góry i nazwa użytkownika w nagłówku ukryte (`HIDE`). Kodowanie i plakat `panel-wideo.jpg` jak przy „Agenci AI”.
