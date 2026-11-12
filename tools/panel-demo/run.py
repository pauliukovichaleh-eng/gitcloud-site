"""Панель my.gitcloud.pl на выдуманных данных (сайт, круг 15, 06.11.2026).
База и сеть отрезаны: db.rows отвечает из fake.py по шаблонам SQL, иначе пусто; исходящие соединения кроме 127.0.0.1 запрещены."""
import os, re, socket, sys
sys.path.insert(0, os.path.dirname(__file__))
_real = socket.socket.connect
def _guard(self, addr):
    h = addr[0] if isinstance(addr, tuple) else addr
    raise OSError("demo: network blocked")
socket.socket.connect = _guard
socket.socket.connect_ex = lambda self, addr: 111
import subprocess
def _nosub(*a, **k): raise FileNotFoundError("demo: no subprocess")
subprocess.run = subprocess.Popen = subprocess.check_output = subprocess.call = _nosub
class Zero(dict):
    def __missing__(self, k): return 0
import fake, fake_llm, fake_dec
from gitcloud_ai import db
def rows(sql, params=None):
    for f in (fake, fake_llm, fake_dec):
        r = f.rows(sql, params)
        if r is not None: return r
    s = " ".join(sql.split()).upper()
    if re.match(r"SELECT (COUNT|SUM|MAX|MIN|AVG)\(", s) and "GROUP BY" not in s: return [Zero()]
    if os.environ.get("DEMO_LOG"): print("SQL∅", s[:160], file=sys.stderr)
    return []
db.rows = rows
db.one = lambda sql, params=None: (rows(sql, params) or [{}])[0]
def _nc(*a, **k): raise RuntimeError("demo: no db")
db.conn = _nc
fake.patch()
fake_llm.patch()
fake_dec.patch()
# DEMO_LANG=pl (tools/pulpit): język bez ciasteczka — okna pulpitu mają własne magazyny ciasteczek
if (_dl := os.environ.get("DEMO_LANG")):
    from gitcloud_core import i18n
    _lo, _cl = i18n.lang_of, i18n.cookie_lang
    i18n.lang_of = lambda cookies, langs: _lo(cookies, langs) if (cookies or {}).get(i18n.COOKIE) else (_dl if _dl in langs else _lo(cookies, langs))
    i18n.cookie_lang = lambda header, langs: _cl(header, langs) if i18n.COOKIE + "=" in (header or "") else (_dl if _dl in langs else _cl(header, langs))
import uvicorn
from gitcloud_ai.app import app
# DEMO_INIT=1 (tools/pulpit): skrypt rolik_common.init() (polskie napisy, ukrycie prywatnego) wklejony w każdą stronę HTML —
# okno pulpitu (WebKit) nie ma add_init_script jak Playwright
if os.environ.get("DEMO_INIT"):
    from rolik_common import init as _init
    _tag = ("<script>" + _init(css="#fcur{display:none !important}") + "</script>").encode()   # kursor rysuje grim

    class _Inject:
        def __init__(self, a): self.a = a
        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                return await self.a(scope, receive, send)
            st = {}
            async def snd(m):
                if m["type"] == "http.response.start":
                    st["m"] = m; st["html"] = any(k == b"content-type" and v.startswith(b"text/html") for k, v in m["headers"]); st["b"] = b""
                    if not st["html"]:
                        await send(m)
                    return
                if m["type"] == "http.response.body" and st.get("html"):
                    st["b"] += m.get("body", b"")
                    if m.get("more_body"):
                        return
                    b = st["b"].replace(b"<head>", b"<head>" + _tag, 1) if b"<head>" in st["b"] else _tag + st["b"]
                    h = [(k, v) for k, v in st["m"]["headers"] if k != b"content-length"] + [(b"content-length", str(len(b)).encode())]
                    await send({**st["m"], "headers": h})
                    return await send({"type": "http.response.body", "body": b})
                await send(m)
            return await self.a(scope, receive, snd)
    app = _Inject(app)
uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "18932")), log_level="warning")
