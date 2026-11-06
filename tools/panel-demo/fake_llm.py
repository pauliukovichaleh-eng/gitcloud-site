"""Выдуманные вызовы LLM для страницы «Модели» (/ai-router) демо-панели (круг 17, 06.11.2026).
Имена моделей — публичные названия, приложения и задачи — выдуманные, суммы и балансы — выдуманные."""
import random
import time
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

R = random.Random(489)
NOW = time.time()
WAW = ZoneInfo("Europe/Warsaw")
# (приложение, задача, вызовов в сутки, [(модель, вес)], средний вход, средний выход)
APPS = [
    ("gw/agenci:sally-poczta", "classify", 46, [("groq:openai/gpt-oss-20b", 5), ("google:gemini-3.5-flash-lite", 4), ("claude:haiku", 2)], 900, 60),
    ("gw/agenci:sally-rozmowa", "sally", 38, [("claude:sonnet", 4), ("groq:openai/gpt-oss-120b", 3), ("groq:qwen/qwen3.8-27b", 1)], 2400, 320),
    ("gw/agenci:tony-alarmy", "write_fast", 22, [("cerebras:gpt-oss-120b", 4), ("groq:openai/gpt-oss-120b", 3), ("google:gemini-3.5-flash-lite", 1)], 1600, 260),
    ("gw/agenci:podsumowanie-dnia", "digest", 6, [("claude:sonnet", 3), ("openai:gpt-5-mini", 2), ("google:gemini-3.8-flash", 1)], 5200, 700),
    ("gw/agenci:mark-przeglad", "recheck", 9, [("claude:sonnet", 2), ("groq:openai/gpt-oss-120b", 2), ("openai:gpt-5-mini", 1)], 3800, 420),
    ("gw/agenci:szkola-egzamin", "judge", 18, [("openai:gpt-5-mini", 3), ("groq:openai/gpt-oss-120b", 3), ("cerebras:gpt-oss-120b", 2)], 1400, 150),
    ("gw/agenci:ocena-odpowiedzi", "score", 30, [("claude:haiku", 3), ("groq:openai/gpt-oss-20b", 3), ("google:gemini-3.1-flash-lite", 2), ("ollama:qwen3:4b-instruct", 1)], 700, 40),
    ("glos-asystenta", "voice", 14, [("cerebras:gpt-oss-120b", 4), ("groq:openai/gpt-oss-120b", 3), ("groq:qwen/qwen3.8-27b", 1)], 1100, 90),
    ("gw/agenci:sally-odpowiedzi", "mail_reply", 28, [("openai:gpt-5-mini", 5), ("claude:sonnet", 2)], 12000, 1200),
    ("gw/agenci:opisy-zdjec", "vision", 3, [("openai:gpt-5-mini", 3), ("google:gemini-3.8-flash", 2)], 2600, 180),
]
ERRS = {"groq": (429, "rate limit, przełączono na zapasowy"), "google": (503, "przeciążony, ponowiono"),
        "cerebras": (429, "rate limit"), "openai": (500, "błąd serwera"), "claude": (529, "przeciążony"), "ollama": (0, "timeout")}


def _pick(ms):
    t = R.uniform(0, sum(w for _, w in ms))
    for m, w in ms:
        t -= w
        if t <= 0:
            return m
    return ms[-1][0]


CALLS = []
for d in range(30):
    for app, task, n, ms, tin, tout in APPS:
        for _ in range(max(0, int(n * R.uniform(0.6, 1.3)))):
            ts = NOW - d * 86400 - R.uniform(0, 86400)
            if d == 0 and ts < NOW - 86400:
                continue
            m = _pick(ms)
            p = m.split(":", 1)[0]
            ok = 0 if R.random() < 0.012 else 1
            CALLS.append({"ts": ts, "model": m, "task": task, "app": app, "ok": ok, "code": ERRS[p][0] if not ok else 200,
                          "tin": int(tin * R.uniform(0.5, 1.6)), "tout": 0 if not ok else int(tout * R.uniform(0.4, 1.8)),
                          "ms": int({"cerebras": 600, "groq": 900, "google": 1500, "ollama": 4200}.get(p, 2600) * R.uniform(0.6, 1.8)),
                          "err": ERRS[p][1] if not ok else ""})
# последние сутки: сбоев нет (обычная картина: пульт показывает деньги и качество, а не ошибки)
for c in CALLS:
    if c["ts"] > NOW - 86400:
        c["ok"], c["code"], c["err"] = 1, 200, ""
CALLS.sort(key=lambda c: -c["ts"])

SCORE = [("claude:sonnet", "sally", 412, 3, 0, 1, 2, 0), ("groq:openai/gpt-oss-120b", "sally", 288, 9, 1, 3, 6, 1),
         ("cerebras:gpt-oss-120b", "write_fast", 341, 5, 0, 2, 3, 0), ("groq:openai/gpt-oss-20b", "classify", 905, 31, 0, 12, 20, 2),
         ("google:gemini-3.5-flash-lite", "classify", 610, 18, 2, 9, 11, 1), ("claude:haiku", "score", 520, 4, 0, 1, 2, 0),
         ("openai:gpt-5-mini", "judge", 230, 2, 0, 0, 1, 0), ("groq:qwen/qwen3.8-27b", "sally", 96, 7, 1, 4, 5, 1),
         ("ollama:qwen3:4b-instruct", "score", 140, 19, 0, 8, 9, 2), ("google:gemini-3.8-flash", "digest", 75, 1, 0, 0, 1, 0)]


def _since(h):
    return [c for c in CALLS if c["ts"] > NOW - h * 3600]


def _day(ts):
    return datetime.fromtimestamp(ts, WAW).strftime("%Y-%m-%d")


def rows(sql, params=None):
    s = " ".join(sql.split()).lower()
    if "from llm_limits" in s:
        return []
    if "from model_score" in s:
        return [dict(zip(("model", "task", "answers", "errors", "refuse", "broken", "doubt", "exam_fail"), x), live_answers=0) for x in SCORE]
    if "from llm_calls" not in s:
        return None
    if s.startswith("select to_char"):
        g = defaultdict(lambda: {"n": 0, "err": 0, "tin": 0, "tout": 0})
        for c in _since(30 * 24):
            x = g[(_day(c["ts"]), c["model"])]
            x["n"] += 1; x["err"] += 1 - c["ok"]; x["tin"] += c["tin"]; x["tout"] += c["tout"]
        return [{"day": d, "model": m, **v} for (d, m), v in g.items()]
    if s.startswith("select count(*) n"):
        cs = _since(24)
        return [{"n": len(cs), "err": sum(1 - c["ok"] for c in cs)}]
    if s.startswith("select app, task, array_agg"):
        g = defaultdict(list)
        for c in _since(7 * 24):
            g[(c["app"], c["task"])].append(c)
        out = [{"app": a, "task": t, "models": sorted({c["model"] for c in cs}), "n": len(cs), "err": sum(1 - c["ok"] for c in cs),
                "tin": sum(c["tin"] for c in cs), "tout": sum(c["tout"] for c in cs), "ms": int(sum(c["ms"] for c in cs) / len(cs)),
                "last": max(c["ts"] for c in cs)} for (a, t), cs in g.items()]
        return sorted(out, key=lambda r: -r["n"])
    if "= any(" in s:
        names = set(params[1])
        g = defaultdict(lambda: {"tin": 0, "tout": 0})
        for c in _since(7 * 24):
            if c["model"].split(":", 1)[1] in names:
                x = g[(c["app"], c["task"], c["model"])]
                x["tin"] += c["tin"]; x["tout"] += c["tout"]
        return [{"app": a, "task": t, "model": m, **v} for (a, t, m), v in g.items()]
    if "limit 60" in s:
        return [dict(c) for c in CALLS[:60]]
    return []


def status():
    """Как llm_router.status(): провайдеры → модели с остатком запросов и токенов за сутки (выдуманные лимиты)."""
    today = _since(24)
    lim = {"groq:openai/gpt-oss-120b": (1000, 200000), "groq:openai/gpt-oss-20b": (1000, 200000), "groq:qwen/qwen3.8-27b": (1000, 300000),
           "cerebras:gpt-oss-120b": (14400, 1000000), "google:gemini-3.5-flash-lite": (1000, None), "google:gemini-3.8-flash": (250, None),
           "google:gemini-3.1-flash-lite": (1000, None), "openai:gpt-5-mini": (None, None), "claude:haiku": (None, None),
           "claude:sonnet": (None, None), "ollama:qwen3:4b-instruct": (None, None)}
    out = defaultdict(list)
    for m, (rl, tpd) in lim.items():
        cs = [c for c in today if c["model"] == m]
        used = sum(c["tin"] + c["tout"] for c in cs)
        out[m.split(":", 1)[0]].append({"id": m, "req": len(cs), "ok": sum(c["ok"] for c in cs), "tin": used, "tout": 0,
                                        "req_lim": rl, "req_left": rl - len(cs) if rl else None,
                                        "tok_left": max(0, tpd - used) if tpd else None, "state": "ok", "reason": ""})
    return [{"name": p, "models": ms} for p, ms in out.items()]


BALANCES = [{"name": "Anthropic API", "usd": 12.40, "how": "wpisano 01.11"},
            {"name": "OpenAI", "usd": 7.85, "how": "doładowano $10, wydano $2.15"},
            {"name": "OpenRouter", "usd": 4.92, "how": "na żywo, konto 1: $4.92"},
            {"name": "Cerebras", "usd": 9.30, "how": "$10 w panelu 20.10, zużycie $0.70 (szacunek)"}]
NIGHT = [{"day": _day(NOW - 86400), "reviewed": ["app-web", "automatyzacje", "panel", "pilot"], "n_findings": 2, "n_fixed": 2,
          "n_pending": 0, "n_high": 0, "repos": []}]


def patch():
    import llm_router
    llm_router.status = status
    llm_router.paid_costs = lambda *a, **k: None
    llm_router.balances = lambda *a, **k: {}
    try:
        from llm_router import claude
        claude.usage = lambda *a, **k: {"lw": 34}
    except ImportError:
        pass
    from gitcloud_ai import router, sources, codereview
    router.balances = lambda: [dict(b) for b in BALANCES]
    router._LIVE.update(at=0.0, rows=[])
    sources.probes = lambda *a, **k: []
    codereview.nights = lambda limit=14: NIGHT[:limit]
