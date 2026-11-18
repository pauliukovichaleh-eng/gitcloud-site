"""Wymyślone dane strony «Bezpieczeństwo» (/bezopasnost) demo-panelu: ochrona hosta, tarcza wiadomości, listy phishingu,
dziennik złapanych wiadomości. Nadawcy, domeny i liczby wymyślone; ochrona mieszkania bez zdarzeń (na zrzutach ukryta) (warsztat strony, 18.11.2026)."""
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)
# listy z pilota: [rodzaj, podpis, wartość, poziom], rodzaj 1 = nagłówek (gitcloud_ai.metrics.groups)
LISTS = {
    "cl": [[1, "ЗАЩИТА ХОСТА", "", 0], [0, "fail2ban", "aktywny, 3 jail", 1], [0, "Банов всего", "41", 0],
           [0, "SSH: неудачных за 24 ч", "0", 1], [0, "Файрвол Proxmox", "włączony", 1],
           [1, "ПРОВЕРКИ", "", 0], [0, "AIDE (целостность)", "bez zmian · 03:10", 1], [0, "Lynis (аудит)", "indeks 78", 1],
           [0, "Копия баз (Postgres)", "dziś 02:40", 1], [0, "Копия OPNsense", "dziś 02:55", 1],
           [0, "Terraform: облако = код", "bez różnic", 1],
           [1, "АУДИТ ФАЙРВОЛА", "", 0], [0, "Последний аудит", "pn 06:30", 1], [0, "В норме / известные исключения", "38 / 2", 1],
           [1, "ОБНОВЛЕНИЯ И КЛЮЧИ", "", 0], [0, "Пакеты хоста", "4 do aktualizacji", 2], [0, "Сертификат Proxmox", "71 dni", 1]],
    "ol": [[1, "ЗАЩИТА", "", 0], [0, "Угрозы (bl_threat_ips)", "1 284", 1], [0, "Соединения (pf states)", "612", 0],
           [0, "DNS (Unbound)", "zablokowano dziś 37", 1]],
}
# dziennik tarczy: (godzin temu, kanał, poziom, nadawca, powód, zdjęte)
JOURNAL = [
    (5, "mail", "danger", "powiadomienia@paczka-doplata.example", "dopłata do przesyłki, link na domenę z listy phishingu", False),
    (29, "wa", "danger", "+48 ••• ••• 117", "kupujący z ogłoszenia: własny kurier i zapłata przed wysyłką", False),
    (52, "mail", "warn", "faktury@biuro-rachunkowe.example", "załącznik .zip z fakturą od nieznanego nadawcy", False),
    (77, "aimail", "warn", "rekrutacja@oferty-zdalne.example", "skrócony link i prośba o dane logowania", False),
    (130, "mail", "warn", "newsletter@sklep-narzedzia.example", "marka w obcej domenie", True),
    (188, "wa", "danger", "+48 ••• ••• 302", "kod BLIK na prośbę znajomego z nowego numeru", False),
    (260, "mail", "danger", "security@konto-weryfikacja.example", "punycode w adresie strony logowania", False),
]
FEEDS = [("cert_pl", 48210, 0.6), ("openphish", 1873, 0.4), ("phishdb", 412306, 2.1), ("shield", 64, 0.4)]


def rows(sql, params=None):
    s = " ".join(sql.split()).lower()
    if "from remote_lists" in s:
        key = (params or ("",))[0]
        return [{"rows": LISTS[key]}] if key in LISTS else []
    if "from metrics_current" in s and (params or ("",))[0] in LISTS:
        return [{"a": 45}]
    if "from msg_shield" in s and "count(*) filter" in s:
        return [{"day": 214, "danger": sum(1 for j in JOURNAL if j[0] < 168 and j[2] == "danger"),
                 "warn": sum(1 for j in JOURNAL if j[0] < 168 and j[2] == "warn"), "ads": 23, "idle": 40.0}]
    if "from bad_domains" in s:
        return [{"src": a, "n": n, "age": h * 3600} for a, n, h in FEEDS]
    if s.startswith("select ref, src, level, label") and "from msg_shield" in s:     # shield_run.journal
        return [{"ref": f"{src}:demo{i}", "src": src, "level": "ok" if off else lvl, "label": "" if off else why,
                 "reasons": [why], "sender": who, "msg_at": NOW - timedelta(hours=h),
                 "allowed_at": NOW - timedelta(hours=h - 3) if off else None}
                for i, (h, src, lvl, who, why, off) in enumerate(JOURNAL)]
    return None


def patch():
    from gitcloud_core import homeguard
    homeguard.recent = lambda *a, **k: []          # ochrona mieszkania: bez zdarzeń, bez zdjęć
    homeguard.paused = lambda *a, **k: None
    from gitcloud_ai import overview
    overview.presence_away = lambda: {"work"}
    from gitcloud_core import presence
    presence.place = lambda *a, **k: "work"

