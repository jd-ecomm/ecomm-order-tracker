# Ecomm Order Tracker

Open ecomm orders for JD Sports Canada, compared with what is usual for the same weekday and hour, with store-level ranking, trends, repeat offenders and regional roll-ups. The live page is a Claude artifact (Ecomm Order Tracker); this repo holds its source, font, baseline maths, data exports and the scheduled task that refreshes it.

## Refresh timings

| What | When (Pacific time) | Notes |
| --- | --- | --- |
| Source report: VCS_JDSF Open Order Snapshot | Hourly, about :05 past the hour, 3am to 9pm, every day | Emailed xlsx from reports@jdcanada.ca (sheet 1 by site, sheet 2 by region) |
| Tracker refresh + Slack update | Monday to Friday, **9:10am, 12:10pm, 4:10pm** | Scheduled Claude task, cron `10 9,12,16 * * 1-5` (America/Vancouver). The evening update moved from 5:10pm to 4:10pm on 3 Nov 2026 so it runs while the laptop is open. |
| Snapshots shown in the tracker picker | **9am, 12pm and 4pm** each day (5pm before 3 Nov 2026) | Other hours feed the intraday chart only |
| GitHub Pages refresh (this site) | Monday to Friday, **about 10am, 1pm and 5pm PT** (task runs 9:50am, 12:50pm, 4:50pm) | Cloud scheduled task pushes `data/tracker.json` with git (no laptop needed). The page shows the 9am, 12pm and 4pm updates |
| Backfill | Every run | Missing hourly snapshots from the last 24h, and run records for missed 9am / 12pm / 5pm snapshots |
| Monday 9:10am run | Weekly | Adds a line on Saturday and Sunday 5pm open orders vs usual |
| Stat holidays | Excluded from "usual" | 12 Oct, 11 Nov, 25 Dec, 26 Dec 2026, 1 Jan 2027 (see `baseline.py`) |

Each run:
1. Reads the newest Open Order Snapshot from Gmail (attachment parsed in the browser) and backfills missing snapshots.
2. Writes company totals to the `snapshots` collection (one doc per hour, id = UTC `YYYY-MM-DDTHHMM`).
3. Writes a `runs` record: watch-list stores, three observations, every site's figures and the four region rows.
4. Updates `meta/latest` and sends a Slack DM: KPIs vs usual, a verdict line, a watch list and Observation 1, 2 and 3.

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
