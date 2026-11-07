# Nocne prowadzenie strony (decyzja #748, 07.11.2026)

Co noc o 04:40 `~/src/gitcloud-remote/host/site-refresh` sprawdza, co zmieniło się od ostatniego udanego odświeżenia
w źródłach tego, co widać na stronie, i przenagrywa tylko to, dopisuje dziennik zmian `/zmiany/` (src/data/zmiany.json, obrazy przed/po w
public/img/zmiany/) i aktualizuje plan `PLAN.md`. Bez zmian w żadnym repo: nic nie robi. Instrukcja dla Claude:
`~/src/gitcloud-remote/host/site-refresh.prompt.md`; jego commity mają trailer `Nocne-odswiezanie: tak`.

| Grupa  | Źródło (repo: ścieżki)                                         | Pliki na stronie                                              | Narzędzie |
|--------|----------------------------------------------------------------|---------------------------------------------------------------|-----------|
| glowy  | gitcloud-remote: head/ (bez dist/)                             | img/agenci/*.webp, projekty/glowa-*, glowy*, mini/glowa-*     | tools/glowy/clip.py |
| pilot  | gitcloud-remote: firmware/src, sim/                            | projekty/pilot-*, pilot.mp4                                   | tools/pilot/render.py, rolik.py |
| panel  | gitcloud-ai: gitcloud_ai/templates, static, i18n               | projekty/panel-*, agenci*, panel.mp4, okładki                 | tools/panel-demo (README) |
| isp    | gitcloud: wszystko poza docs/ i tests/                         | img/demo/*.webp                                               | tools/isp/shoot.py |

Zasady: plik podmieniany tylko, gdy kadr widocznie się zmienił (bez zmian = stary plik zostaje, repo nie puchnie);
tylko dane przykładowe; `npm run build` (check.mjs) musi przejść. Wynik idzie od razu na main (GitHub Pages),
rano jedna linia w podsumowaniu. Miniatury i plakaty (img/mini, img/plakat) odtwarza `node tools/miniatury.mjs`.
