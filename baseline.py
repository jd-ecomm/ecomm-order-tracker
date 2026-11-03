from datetime import datetime
from zoneinfo import ZoneInfo
TZ = ZoneInfo("America/Vancouver")
HOLIDAYS = {"2026-10-12", "2026-11-11", "2026-12-25", "2026-12-26", "2027-01-01"}
GROUPS = {5: "wkend", 6: "wkend", 0: "mon", 1: "mid", 2: "mid", 3: "mid", 4: "fri"}
PCT = {"otToday", "otMTD", "declRate"}
def _local(ts): return datetime.fromtimestamp(ts / 1000, TZ)
def expected(rows, k, now_ts):
    now = _local(now_ts); h, today = now.hour, now.date()
    by_day = {}
    for r in rows:
        t = _local(r["ts"])
        if t.hour == h and t.date() != today and str(t.date()) not in HOLIDAYS and r.get(k) is not None:
            by_day[t.date()] = r[k]
    if not by_day: return None, 0
    if k in PCT:
        vals = [v for d, v in by_day.items() if 0 < (today - d).days <= 7]
        return (sum(vals) / len(vals) if vals else None), 0
    ratios = {}
    for d, v in by_day.items():
        win = [x for dd, x in by_day.items() if abs((dd - d).days) <= 3]
        if len(win) >= 4 and sum(win) > 0:
            ratios.setdefault(d.weekday(), []).append(v / (sum(win) / len(win)))
    grp = {}
    for wd, rs in ratios.items(): grp.setdefault(GROUPS[wd], []).extend(rs)
    def factor(wd):
        if len(ratios.get(wd, [])) >= 2: return sum(ratios[wd]) / len(ratios[wd])
        g = grp.get(GROUPS[wd], [])
        return sum(g) / len(g) if g else 1.0
    recent = [(d, v) for d, v in by_day.items() if 0 < (today - d).days <= 7]
    if not recent: return None, 0
    level = sum(v / factor(d.weekday()) for d, v in recent) / len(recent)
    n_same = len([d for d in by_day if d.weekday() == today.weekday()])
    return level * factor(today.weekday()), n_same
