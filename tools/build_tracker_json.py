"""Rebuild data/tracker.json for the GitHub Pages copy from an ArtifactData export.
Usage: python3 tools/build_tracker_json.py <export-dir>   (export-dir holds snapshots/, runs/, meta/ JSON files)"""
import json, glob, os, sys, datetime
W = sys.argv[1]
d = json.load(open('data/tracker.json'))
L = lambda p: json.load(open(p))
strip = lambda x: {k: v for k, v in (x.get('data', x) if isinstance(x.get('data'), dict) else x).items() if k not in ('id', 'version')}
snaps = sorted((strip(L(p)) for p in glob.glob(f'{W}/snapshots/*.json')), key=lambda s: -s['ts'])
runs = dict(d['runs'])
for p in glob.glob(f'{W}/runs/*.json'): runs[os.path.basename(p)[:-5]] = strip(L(p))
cut = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=8)).strftime('%Y-%m-%d')
runs = {k: runs[k] for k in sorted(runs) if k >= cut}
latest = strip(L(f'{W}/meta/latest.json')); st = L(f'{W}/meta/stores.json'); st = st.get('data', st); stores = st.get('info', st)
assert len(snaps) > 400 and len(runs) > 10 and len(stores) >= 45, (len(snaps), len(runs), len(stores))
json.dump({'generated': snaps[0]['ts'], 'snapshots': snaps, 'runs': runs, 'latest': latest, 'stores': stores}, open('data/tracker.json', 'w'), separators=(',', ':'))
print(len(snaps), 'snapshots,', len(runs), 'runs, newest', datetime.datetime.fromtimestamp(snaps[0]['ts'] / 1000, datetime.timezone.utc).isoformat())
