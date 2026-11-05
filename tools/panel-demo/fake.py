"""Выдуманные данные для демо-панели (06.11.2026): журнал дел агентов на польском, без реальных систем и людей."""
import random
from datetime import datetime, timedelta, timezone

R = random.Random(437)
NOW = datetime.now(timezone.utc)
T = {
    "tony": [("fix", "Restart usługi app-web po alarmie pamięci", "ndfix", "Pamięć wróciła do 41 %"),
             ("check", "Kopie zapasowe bazy: test odtworzenia", "night", "Odtworzenie w 3 min 12 s, sumy zgodne"),
             ("fix", "Wyczyszczony katalog tymczasowy przeglądarki", "logdoctor", "Zwolnione 2,1 GB"),
             ("check", "Certyfikaty TLS: ważność", "night", "Wszystkie ważne ponad 30 dni"),
             ("fix", "Rotacja dzienników usługi automatyzacji", "logdoctor", "Dziennik z 1,4 GB do 120 MB"),
             ("check", "Aktualizacje pakietów na serwerze testowym", "night", "12 pakietów, bez restartu"),
             ("decide", "Alarm obciążenia CPU: chwilowy, bez akcji", "ndfix", "Skok 3 min przy kompilacji"),
             ("fix", "Ponowione zadanie harmonogramu: raport dzienny", "night", "Raport gotowy o 05:12"),
             ("handoff", "Dysk zewnętrzny: wymiana wymaga człowieka", "ndfix", "Karta w panelu z wariantami")],
    "sally": [("check", "Przegląd skrzynki: 9 wiadomości", "sally", "2 sprawy do kalendarza, reszta archiwum"),
              ("send", "Przypomnienie o terminie płatności faktury testowej", "sally", "Termin w panelu"),
              ("decide", "Spotkanie przeniesione na czwartek 10:00", "sally", "Kalendarz zaktualizowany"),
              ("check", "Uzgodnienie wydatków miesiąca", "sally", "Zgodne z wyciągiem, 0 różnic"),
              ("close", "Zamknięta sprawa: odnowienie domeny demo", "sally", "Opłacone, ważne do 2027"),
              ("send", "Poranne podsumowanie dnia", "sally", "6 punktów, 1 do decyzji"),
              ("handoff", "Wybór oferty hostingu: dwa warianty", "sally", "Karta decyzji w panelu")],
    "mark": [("check", "Przegląd zależności: 4 repozytoria", "mark", "2 aktualizacje bezpieczeństwa"),
             ("decide", "Propozycja: cache zapytań panelu", "mark", "Rada agentów: tak, 3 z 3"),
             ("fix", "Aktualizacja biblioteki HTTP w repozytorium demo", "mark", "Testy zielone, 41 z 41"),
             ("check", "Nocny przegląd kodu", "review", "Znaleziska 2, naprawione 2"),
             ("fix", "Szybsza strona statusu: 4,7 s do 0,3 s", "mark", "Pomiar przed i po w dzienniku"),
             ("handoff", "Migracja bazy na nową wersję: zgoda właściciela", "mark", "Karta z planem i ryzykiem")],
}
ACTIONS = []
_id = 1
for d in range(14):
    for agent, pool in T.items():
        for _ in range(R.choice([1, 2, 2, 3, 3, 4]) if agent != "mark" else R.choice([0, 1, 1, 2])):
            kind, title, src, res = R.choice(pool)
            at = (NOW - timedelta(days=d)).replace(hour=R.choice([2, 3, 4, 6, 7, 9, 11, 14, 16, 19, 22]), minute=R.randrange(60))
            if at > NOW:
                at -= timedelta(hours=12)
            ok = None if kind == "handoff" else (False if R.random() < 0.06 else True)
            ACTIONS.append({"id": _id, "at": at, "agent": agent, "kind": kind, "title": title, "why": "", "result": res,
                            "ok": ok, "source": src, "ref": "", "steps": []})
            _id += 1
for i, (ag, k) in enumerate([("tony", 0), ("sally", 0), ("tony", 3), ("mark", 1), ("sally", 5)]):
    kind, title, src, res = T[ag][k]
    ACTIONS.append({"id": _id + i, "at": NOW - timedelta(minutes=7 + 9 * i), "agent": ag, "kind": kind, "title": title,
                    "why": "", "result": res, "ok": True, "source": src, "ref": "", "steps": []})
ACTIONS.sort(key=lambda a: a["at"], reverse=True)


def _since(h):
    return [a for a in ACTIONS if a["at"] > NOW - timedelta(hours=h)]


def rows(sql, params=None):
    s = " ".join(sql.split()).lower()
    if "from agent_actions" not in s:
        return None
    if s.startswith("select a.agent, a.kind, a.ok"):
        return [{**a, "solved": a["ok"] is False} for a in _since(24)]
    if "where agent = %s" in s:
        ag, days = params
        return [a for a in _since(24 * int(days)) if a["agent"] == ag]
    if s.startswith("select kind, ok, count(*)"):
        from collections import Counter
        c = Counter((a["kind"], a["ok"]) for a in _since(24))
        return [{"kind": k, "ok": o, "n": n} for (k, o), n in c.items()]
    if "ok is false" in s:
        return [a for a in _since(24) if a["ok"] is False][:1]
    if "agent = 'tony'" in s:
        return [a for a in _since(24) if a["agent"] == "tony"]
    return []


def patch():
    from gitcloud_ai import sources
    sources.netdata_active = lambda *a, **k: []
    sources.netdata_log = lambda *a, **k: []
    from gitcloud_ai import app
    app.now_important = lambda *a, **k: {"show": False, "items": []}
    app.personal_line = lambda *a, **k: [{"lvl": "ok", "text": "✓ Всё спокойно", "href": "/", "kind": ""}]
