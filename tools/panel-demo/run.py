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
import uvicorn
from gitcloud_ai.app import app
uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "18932")), log_level="warning")
