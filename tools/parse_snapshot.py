"""Parse a VCS_JDSF Open Order Snapshot email (Gmail RAW json) into tracker numbers.
Usage: python3 parse_snapshot.py <gmail_raw.json> -> prints JSON {ts, company, sites, regions}"""
import json, sys, base64, email, io, zipfile, re, html, math
def load(path):
    d = json.load(open(path)); raw = d['raw']
    b = base64.urlsafe_b64decode(raw + '=' * (-len(raw) % 4))
    m = email.message_from_bytes(b)
    for p in m.walk():
        fn = p.get_filename()
        if fn and fn.endswith('.xlsx'): return d, p.get_payload(decode=True)
    sys.exit('no xlsx attachment')
def sheets(x):
    z = zipfile.ZipFile(io.BytesIO(x)); ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in re.findall(r'<si>([\s\S]*?)</si>', z.read('xl/sharedStrings.xml').decode()):
            ss.append(html.unescape(''.join(re.findall(r'<t[^>]*>([\s\S]*?)</t>', si))))
    out = {}
    for n in sorted(k for k in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', k)):
        rows = []
        for r in re.findall(r'<row[\s\S]*?</row>', z.read(n).decode()):
            row = {}
            for c in re.findall(r'<c [^>]*?(?:/>|>[\s\S]*?</c>)', r):
                ref = re.search(r'r="([A-Z]+)', c).group(1); t = re.search(r' t="(\w+)"', c)
                v = re.search(r'<v>([\s\S]*?)</v>', c)
                v = v.group(1) if v else ''.join(re.findall(r'<t[^>]*>([\s\S]*?)</t>', c))
                v = html.unescape(v)
                if t and t.group(1) == 's': v = ss[int(v)]
                row[ref] = v
            rows.append(row)
        out[n.split('/')[-1][:-4]] = rows
    return out
def num(v):
    try: return float(str(v).replace(',', '').replace('$', '').replace('%', ''))
    except: return None
d, x = load(sys.argv[1]); S = sheets(x)
H = d['id']; ts = (int(H, 16) >> 20) // 60000 * 60000
reg = {r.get('A'): r for r in S['sheet2'] if r.get('A')}
def rowarr(r): return [r.get('A'), num(r.get('G')), int(math.floor((num(r.get("I")) or 0)+0.5)), num(r.get('R')), num(r.get('O')), num(r.get('Q')), num(r.get('P')), num(r.get('E')), num(r.get('F'))]
ct = reg['Company Total']
company = dict(open=num(ct['G']), val=num(ct['I']), gt3=num(ct['E']), hold=num(ct['F']), otMTD=num(ct['J']), shippedMTD=num(ct.get('K')),
    declRate=num(ct['O']), shipToday=num(ct['P']), otToday=num(ct.get('Q')), declToday=num(ct['R']),
    wOpen=num(reg['Warehouse Total']['G']), sOpen=num(reg['Store Total']['G']), wDecl=num(reg['Warehouse Total']['R']), sDecl=num(reg['Store Total']['R']), ts=ts)
sites = [rowarr(r) for r in S['sheet1'][3:] if r.get('A') and r.get('A') != 'Total']
regions = [rowarr(reg[k]) for k in ('BC', 'Prairies', 'ON', 'QC and Atlantic') if k in reg]
print(json.dumps(dict(ts=ts, company=company, sites=sites, regions=regions)))
