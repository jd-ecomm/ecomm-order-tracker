# Scheduled task: Ecomm Order Tracker (open orders to Slack)

- Schedule: `CRON_TZ=America/Vancouver 10 9,12,17 * * 1-5` (9:10am, 12:10pm, 5:10pm PT, Monday to Friday)
- Runs in a fresh Claude session; needs Ryan's computer (built-in browser signed in to Gmail) for the xlsx attachment.
- Writes only to the Ecomm Order Tracker artifact database and Ryan's own Slack DM.

## Instructions (as stored, 3 Nov 2026)

Job: read the latest "VCS_JDSF - Open Order Snapshot" email attachment, log it to the Ecomm Order Tracker artifact, compare it with what's usual for this weekday and hour, and DM Ryan a short update in Slack.

Rules: Canadian English. No em dashes. End the update with three numbered observations (**Observation 1:**, **Observation 2:**, **Observation 3:**), one sentence each, most important first, naming specific stores or sites and numbers. Never use the labels What, So What or What's Next. Never email, reply to, label, archive or trash any email. Never message anyone but Ryan. Compute every figure, baseline and % change in Python before writing and double-check against the source. America/Vancouver is on permanent UTC-7 in the environment's tz data, so the 9am, 12pm and 5pm PT snapshots are the emails at about 16:05, 19:05 and 00:05 UTC.

### 1. Find the latest snapshot
Gmail `search_threads` `from:reports@jdcanada.ca subject:"Open Order Snapshot" newer_than:1d`, then `get_thread` (METADATA_ONLY) on the newest thread and take the latest message (hex id H). Emails arrive about :05 past each hour, 3am to 9pm PT. If nothing newer than 3 hours exists, say so in the DM and stop. Also check `subject:"Completed Count Alert"` (store inventory counts) and mention any new one in one line.

### 2. Read the xlsx (built-in browser)
Open Gmail in the built-in browser, get the `ik` value, and fetch
`https://mail.google.com/mail/u/0?ui=2&ik=<IK>&attid=0.1&permmsgid=msg-f:<BigInt('0x'+H)>&th=<H>&view=att&zw&disp=safe`.
Parse it in-page with a regex-only xlsx reader (Gmail uses Trusted Types). Sheet 1 = by site (A site, B <24h, C 1-2d, D 2-3d, E >3d, F on hold, G total open, H open %, I value, J on-time % MTD, K shipped MTD, N declines MTD, O decline rate MTD, P shipped today, Q on-time % today, R declines today; warehouses Coquitlam and Flint; exclude the Total row). Sheet 2 = regions BC, Prairies, ON, QC and Atlantic, then Store Total, Warehouse Total, Company Total.
Company Total gives open, val, gt3, hold, otMTD, shippedMTD, declRate, shipToday, otToday, declToday; wOpen / sOpen from Warehouse / Store Total. ts = H >> 20 (ms), floored to the minute. Return compact arrays [name, G, I, R, O, Q, P, E, F] for every site and region row.

### 3. Log and compute baselines
- Read `snapshots`; backfill missing hourly snapshots from the last 24h.
- Open % of 24h orders with `openpct.py` over all rows.
- Write new snapshots (`set`, id = UTC `YYYY-MM-DDTHHMM`) and openPct updates in one batch.
- "Usual" for open, openPct, val, gt3, hold, otToday, declToday with `baseline.py`. Verdict: above +10% more than usual, below -10% less, otherwise normal.
- Monday 9:10 run: weekend line (Sat and Sun 5pm vs usual).
- Run record `runs/{id}`: {ts, sites (top 3 by open, every flagged store, top decliners, max 12), observations, allSites, regions}. Backfill run records for missed 9am / 12pm / 5pm snapshots in the last 24h. Add any new site to `meta/stores`.
- Use run history in observations (repeat offenders, stores rising across the last 3 updates).
- Update `meta/latest` with {ts, sites, observations}.

### 4. Slack DM (to Ryan only)
Bullets: open orders vs usual, open % of 24h orders, aged over 3 days, on hold, on-time ship today, declines today (warehouse / stores), split, fiscal MTD. Then one bold verdict line (count and share together: backlog building / higher volume being cleared / slower shipping / tracking as normal), "Watch:" bullets when stores are flagged, Observation 1 to 3, and the tracker link with the next update time. Never send invented figures; if something fails, DM what failed.
