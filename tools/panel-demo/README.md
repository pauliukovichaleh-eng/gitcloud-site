# Zrzuty panelu agentów na danych przykładowych

Panel (prywatne repozytorium gitcloud-ai) uruchomiony bez bazy i bez sieci: `run.py` odcina połączenia wychodzące
i podprocesy, zapytania SQL obsługuje `fake.py` (wymyślony dziennik spraw agentów), resztę zwraca pustą.

    cd ~/src/gitcloud-ai && PORT=18932 .venv/bin/python <repo>/tools/panel-demo/run.py &
    python final.py http://my.gitcloud.pl:18932 <katalog>    # Playwright, Chrome z MAP my.gitcloud.pl 127.0.0.1

`final.py` tłumaczy kilka brakujących napisów na polski i sprawdza, czy w kadrze nie ma cyrylicy.
Obrazy: PNG → WebP (jakość 82) do public/img/projekty/panel-*.webp.

Strona modeli (`/ai-router`): `fake_llm.py` generuje wymyślone wywołania LLM z 30 dni (wymyślone aplikacje agentów,
publiczne nazwy modeli, kwoty i salda przykładowe), wynik jakości modeli i limity; podmienia status bramki LLM,
salda i nocny przegląd kodu. Zrzuty: `python final.py http://my.gitcloud.pl:18932 <katalog> modele`.

Karty decyzji (pulpit Claude na stronie głównej panelu): `fake_dec.py` daje wymyślone pytania agentów do właściciela
z wariantami, dziennik decyzji z wynikami, dwie sesje Claude i limity. Zrzuty samego widżetu:
`python final.py http://my.gitcloud.pl:18932 <katalog> decyzje` (komputer, komputer z rozwiniętymi szczegółami i dziennikiem, telefon).

Okładka karty „Panel operacyjny” (16:9): `tools/okladki/panel.html` składa gotowe zrzuty `panel-decyzje.webp`
(kadr trzech kart) i `panel-decyzje-tel.webp` w ramce okna i telefonu. Zrzut 1280×720 Chrome/Playwright → WebP
(jakość 82) do `public/img/projekty/panel-okladka.webp`.

Okładka karty „Agenci AI” (16:9): `DSF=2 python final.py … <katalog>` (zrzuty /agenty, /agenty/tony, /agenty/sally w 2x)
→ WebP `tools/okladki/agenci-{agenci,tony,sally}-2x.webp`; `tools/okladki/agenci.html` składa pierścień działań,
karty dwóch agentów i wskaźnik „Decydują sami”. Zrzut 1280×720 → WebP (jakość 82) do `public/img/projekty/agenci-okladka.webp`.
