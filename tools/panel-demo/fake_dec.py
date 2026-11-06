"""Выдуманные карточки «Решения» и сессии Claude для пульта Claude на Главной демо-панели (круг 19, 06.11.2026).
Вопросы, варианты, итоги и названия сессий выдуманы; реальных людей, заказчиков и систем нет."""
import time
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)


def _o(*opts):
    return [{"k": str(n), "label": l, "desc": d, "rec": n == 1} for n, (l, d) in enumerate(opts, 1)]


OPEN = [
    ("mark", 6, "Migracja bazy demo na PostgreSQL 18?",
     "Plan w 3 krokach: kopia, migracja w oknie 15 min w niedzielę, test odtworzenia. Ryzyko niskie, testy 41 z 41.",
     _o(("Tak, w niedzielę", "Kopia przed i test odtworzenia po"), ("Za tydzień", "Najpierw próba na kopii"), ("Nie teraz", "Wrócić za miesiąc"))),
    ("handoff_tony", 23, "Dysk zewnętrzny kopii: SMART ostrzega",
     "Tony przeniósł kopie na drugi dysk, wszystkie sumy zgodne. Wymiana dysku wymaga człowieka.",
     _o(("Zamówię nowy dysk", "Tony przypomni, gdy przyjdzie"), ("Przypomnij za 3 dni", ""), ("Zostaw na drugim dysku", "Bez zapasowej kopii lokalnej"))),
    ("sally", 41, "Hosting strony demo: który wariant?",
     "Sally porównała dwie oferty: A szybszy w Europie, B tańszy o 30 % rocznie. Obie z kopią i TLS.",
     _o(("Wariant A", "Niższe opóźnienia dla klientów w PL"), ("Wariant B", "Taniej, wystarczy dla demo"), ("Zostać przy obecnym", ""))),
]
DONE = [  # (źródło, min temu zadane, min do odpowiedzi, pytanie, wybrany, wynik, auto)
    ("claude", 95, 11, "Strona: zrzuty modeli na danych przykładowych?", "Zrzuty modeli", "Zrobione, 2 kadry, testy ok", False),
    ("mark", 180, 4, "Nocny przegląd: 2 znaleziska do naprawy", "Napraw sam", "Naprawione 2 z 2, testy zielone", False),
    ("morning", 420, 0, "Raport dzienny o 05:12 czy o 07:00?", "O 07:00", "Harmonogram zmieniony", True),
    ("handoff_sally", 610, 26, "Spotkanie w czwartek: przenieść na 10:00?", "Tak, 10:00", "Kalendarz zaktualizowany", False),
]
Q = []
for i, (src, m, q, ctx, opts) in enumerate(OPEN):
    Q.append({"id": 900 + i, "at": NOW - timedelta(minutes=m), "source": src, "question": q, "context": ctx, "options": opts,
              "answer": None, "answered_at": None, "applied_at": None, "result": None, "task_result": None, "note": None, "auto": False})
for i, (src, m, dm, q, pick, res, auto) in enumerate(DONE):
    at = NOW - timedelta(minutes=m)
    opts = _o((pick, ""), ("Później", ""))
    Q.append({"id": 880 + i, "at": at, "source": src, "question": q, "context": "", "options": opts, "answer": "1",
              "answered_at": at + timedelta(minutes=dm), "applied_at": at + timedelta(minutes=dm + 2), "result": res,
              "task_result": None, "note": None, "auto": auto})


def rows(sql, params=None):
    s = " ".join(sql.split()).lower()
    if "from owner_questions" not in s:
        return None
    if s.startswith("select id, at, source, question"):
        return [dict(x, options=[dict(o) for o in x["options"]]) for x in Q]
    if "status = 'draft'" in s:
        return [{"n": 1}]
    if "as asked" in s:
        return [{"asked": 6, "auto": 1, "open": len(OPEN)}]
    return []


T = time.time()
SESS = [
    {"id": "s1", "pid": 1, "name": "strona: portfolio", "status": "busy", "since": T - 14 * 60, "label": "в работе", "lvl": "busy",
     "bg": False, "dur": "14 мин", "what": "Zrzuty kart decyzji na danych przykładowych"},
    {"id": "s2", "pid": 2, "name": "panel: szybsza strona statusu", "status": "idle", "since": T - 6 * 60,
     "label": "готово " + time.strftime("%H:%M", time.localtime(T - 6 * 60)), "lvl": "ok", "bg": False, "dur": "",
     "what": "Strona statusu 4,7 s → 0,3 s, testy zielone"},
]


def patch():
    from gitcloud_ai import claudecc
    claudecc.sessions = lambda *a, **k: [dict(s) for s in SESS]
    claudecc.usage = lambda: {"l5": 22, "r5": T + 2.6 * 3600, "lw": 34, "rw": T + 3.2 * 86400, "at": T - 120}
    try:
        from gitcloud_ai import workshop
        workshop.claude_rows = lambda *a, **k: []
    except ImportError:
        pass
