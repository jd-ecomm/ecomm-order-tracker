# Ecomm Order Tracker

Open ecomm orders for JD Sports Canada, compared with what is usual for the same weekday and hour, with store-level ranking, trends, repeat offenders and regional roll-ups. The live page is a Claude artifact (Ecomm Order Tracker); this repo holds its source, font, baseline maths, data exports and the scheduled task that refreshes it.

## Refresh timings

| What | When (Vancouver) | How |
|---|---|---|
| Hourly tracker update | Monday to Friday, every hour 9:12am to 5:12pm | Cloud scheduled task "Ecomm Order Tracker (cloud)". Reads the newest VCS_JDSF Open Order Snapshot email straight from Gmail (raw message, attachment parsed by `tools/parse_snapshot.py`), logs it to the artifact database, then rebuilds `data/tracker.json` (`tools/build_tracker_json.py`) and pushes it. No laptop needed. Started 6 Nov 2026 |
| Observations + Slack update | 10:12am, 1:12pm, 5:12pm (the 10am, 1pm and 5pm snapshots) | Same task: run record, watch list, three observations, meta/latest and the Slack DM |
| Earlier schedule | Before 6 Nov 2026 | Work-PC task at 9:10am, 12:10pm and 4:10pm (5:10pm before 3 Nov), GitHub copy at 9:50, 12:50, 4:50 |
| Backfill | Every run | Missing hourly snapshots from the last 24h |
| Monday 10:12am run | Weekly | Adds a line on Saturday and Sunday 5pm open orders vs usual |
| Stat holidays | Excluded from "usual" | 12 Oct, 11 Nov, 25 Dec, 26 Dec 2026, 1 Jan 2027 (see `baseline.py`) |

## Tracker page (`index.html`)

JD brand baseline v2: Forever Forward Sans Headline display (`ForeverForwardSans-Headline.woff2`), Inter Tight body, JD Yellow #FFDE14, dark mode, Roundel flush right.

- **Picker:** day plus 9am / 12pm / 5pm, with previous / next / latest. KPIs and "usual" are recalculated as of the update you pick.
- **Observations 1 to 3** for the update.
- **Now vs usual:** open orders, open % of 24h orders, value, aged over 3 days, on hold, on-time ship today, declines today, warehouse / store split, fiscal MTD.
- **Intraday chart:** metric switch (open, open %, value, aged, declines), series toggles (selected day, 7-day average, 7-day range, same day last week), hover / tap / keyboard tooltips, click a 9am / 12pm / 5pm point to open it.
- **Watch list** for the update.
- **Stores:**
  - *Ranking:* every site, sortable, region filter, change vs previous update, 7-day sparkline, flagged rows marked.
  - *Store trend:* any site, metric switch, vs average store, flagged updates in red.
  - *Repeat offenders:* stores flagged in the last 7 days, one dot per update, main reasons.
  - *Regions:* BC, Prairies, Ontario, QC & Atlantic from the report's own region rows, with trend and busiest stores.
- **Check-time log:** last 10 days of 9am / 12pm / 5pm readings, click to open.

A store is flagged when it holds 25+ open orders, has 8+ declines today, or has 10+ open orders with nothing shipped today.

The page reads its data through the artifact runtime (`claude.use('db')`), so opening `index.html` outside the artifact shows the offline state; the CSVs in `data/` hold the same data.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | Tracker page source |
| `ForeverForwardSans-Headline.woff2` | JD display font used by the page (the page also looks in `fonts/`) |
| `baseline.py` | "Usual": same PT hour over the last 7 days, scaled by a learned weekday factor. The page runs an identical JavaScript port. |
| `openpct.py` | Open % of 24h orders = open ÷ (open + shipped in last 24h + declined in last 24h) |
| `data/snapshots.csv` | Every logged hourly company snapshot (export of the `snapshots` collection) |
| `data/store_runs.csv` | Every site's figures at each 9am / 12pm / 5pm update from 27 Oct 2026 |
| `data/region_runs.csv` | Region rows at each update |
| `data/stores.csv` | Site code, name, region and province |
| `data/run_notes.json` | Watch lists and observations written by the runs |
| `docs/scheduled-task.md` | The scheduled task's full instructions |

## Data model (artifact database)

- `snapshots/{id}`: `open, val, gt3, hold, shipToday, otToday, declToday, otMTD, declRate, wOpen, sOpen, ts` and, when computable, `ship24, decl24, openPct`.
- `runs/{id}`: `ts, sites[{n, open, val, declToday, declRate, flag, note}], observations[3], allSites[[site, open, value, declToday, declRateMTD, otToday, shipToday, gt3, hold]], regions[[region, ...same]]`.
- `meta/latest`: `ts, sites, observations` for the newest run.
- `meta/stores`: `info{code: {n, region, prov, jd}}`.

## Notes

- Fiscal month-to-date decline rates reset on the 1st; early-month rates can look extreme on small volumes.
- Region placement of the six non-JD sites (1001, 1004, 1005, 1006, 2001, 2002) is inferred from their names.
- This repository is public.
