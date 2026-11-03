from datetime import timedelta
from baseline import _local
def add_open_pct(rows):
    by = {}
    for r in rows:
        t = _local(r["ts"]); by.setdefault(t.date(), {})[t.hour] = r
    out = {}
    for r in rows:
        t = _local(r["ts"])
        prev = by.get(t.date() - timedelta(days=1), {})
        if not prev or t.hour not in prev: continue
        lh = max(prev)
        if lh < 20: continue
        s24 = r["shipToday"] + prev[lh]["shipToday"] - prev[t.hour]["shipToday"]
        d24 = r["declToday"] + prev[lh]["declToday"] - prev[t.hour]["declToday"]
        den = r["open"] + s24 + d24
        if s24 < 0 or d24 < 0 or den <= 0: continue
        out[id(r)] = dict(ship24=s24, decl24=d24, openPct=round(r["open"] / den, 4))
    for r in rows:
        if id(r) in out: r.update(out[id(r)])
    return rows
