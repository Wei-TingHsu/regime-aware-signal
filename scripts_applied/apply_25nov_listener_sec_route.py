"""apply_25nov_listener_sec_route.py -- the listener reads the SEC's single list of the newest filings first (it shows a filing about half a minute before
the company's own list: lag watch of 24 Nov), and leaves research and short-seller sites alone for 2 minutes between looks (one of them refused a look every
15 seconds). TRACK 3.113 records the lag watch, the spread price and this change. Idempotent."""
from pathlib import Path
p = Path("src/news_listener.py"); s = p.read_text(); ok = True
F = '''SEC_CURRENT = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form}&company=&dateb=&owner=include&count=100&output=atom"


def sec_current(by_cik: dict) -> dict:
    """25 Nov 2026 (lag watch, TRACK 3.113): the SEC's single list of the newest filings shows a filing about half a minute before the company's own list does
    (middle 36 s against 73 s after acceptance). -> {source name: [items]} for the companies of the list, in the shape sec_recent gives; the company's own list
    stays as the backup, and a filing seen on both is taken once (same accession number)."""
    out = {}
    for form in ("8-K", "6-K"):
        for it in feed_items(fetch(SEC_CURRENT.format(form=form))):
            m = re.search(r"/data/(\\d+)/", it.get("link", "")); a = re.search(r"(\\d{10})-?(\\d{2})-?(\\d{6})", it.get("link", "").split("/data/")[-1])
            if not m or not a or it["title"].split(" - ")[0].strip().upper() != form or it.get("published") is None: continue
            src = by_cik.get(m.group(1).zfill(10))
            if src is None: continue
            acc = f"{a.group(1)}-{a.group(2)}-{a.group(3)}"; items = ",".join(re.findall(r"Item (\\d+\\.\\d+)", it.get("summary", "")))
            out.setdefault(src, []).append(dict(id=acc, form=form, items=items, accession=acc, primary="", published=it["published"], title=f"{form} items {items or 'n/a'}"))
    return out


'''
if "def sec_current(" in s: print("  news_listener.py: the single SEC list is already read -- skipped")
else:
    a1 = "def sec_text(cik: str, accession: str, primary: str) -> str:"
    a2 = '''            for src in S:
                try: items = poll(src)
'''
    b2 = '''            try: fast = sec_current({x["cik"]: x["name"] for x in S if x["kind"] == "sec"})      # 25 Nov: the SEC's single list first; about half a minute earlier than each company's own list
            except SystemExit: raise
            except Exception: fast = {}
            for src in S:
                if src["kind"] in ("research", "short") and time.time() - src.get("_last", 0) < 120: continue      # 25 Nov: these sites publish a few times a day and one refused a look every 15 s
                src["_last"] = time.time()
                try: items = fast.get(src["name"], []) + poll(src)
'''
    if s.count(a1) == 1 and s.count(a2) == 1: s = s.replace(a1, F + a1).replace(a2, b2); p.write_text(s); print("  news_listener.py: reads the SEC's single list first; research and short-seller sites every 2 minutes (restart the listener)")
    else: ok = False; print(f"  news_listener.py: the expected lines were not found ({s.count(a1)}, {s.count(a2)}) -- NOT changed; tell Claude")
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.113 Lag watch result; the listener's SEC route changed; the price of the spread measurement (25 Nov 11:50)
**Lag watch** (`docs/lag_watch.md`, commit e765849; 24 Nov 12:35 to 14:35 New York, 120 minutes; SEC lists looked at every 5 s, feeds every 15 s). Time from the SEC's acceptance stamp to the filing being visible, 16 filings seen on both addresses:
| SEC address | fastest | middle | nine in ten within | slowest |
|---|---|---|---|---|
| one list for all companies | 17 s | 36 s | 49 s | 78 s |
| the company's own list (what the listener used) | 27 s | 73 s | 86 s | 100 s |
PR Newswire (67 new releases): fastest 48 s, middle 132 s, nine in ten within 188 s, slowest 229 s after its own time stamp. Looks answered: SEC single list 912 and 866 with 0 refusals (4 other failures each); the feeds about 400 each with 0 refusals; **SemiAnalysis refused three looks in a row (HTTP 403)** and was left alone.
**Priors scored.** #171 (the single list is earlier than the company's own list on most filings): RIGHT -- 37 s earlier on the middle filing. #172 (no source refuses at these frequencies): WRONG -- SemiAnalysis did.
**The change, by the rule of 3.83** (`scripts_applied/apply_25nov_listener_sec_route.py`). The listener reads the SEC's single list of the newest 8-K and 6-K filings at the start of every pass and takes the filings of the list's companies from it; each company's own list stays as the backup and a filing seen on both is taken once. Research and short-seller sites are looked at every 2 minutes at most. The listener is to be run with `--poll 15` (15 seconds between passes; the default is 30).
**What this does NOT fix, stated plainly.** The long lags in the live log are not feed lags. On 23 Nov the NVIDIA reinstatement (71-74 minutes), the CrowdStrike filings (about 4 hours) and on 24 Nov the Meta filing (9 hours) were all read in one burst when the listener was started: **the listener was not running when they were published.** With the listener running, the SEC is 36 s and PR Newswire about 2 minutes. The remaining cause is the listener being off -- the always-on server of 3.83, still the founder's open decision -- and for the pool plan (docs/POOL_PLAN.md, point 10) it is the main risk.
**Spread measurement, price** (`python -m src.spread_measure plan`, 25 Nov): 1,756 windows of 10 minutes (712 for stocks, 688 for 1x funds, 356 for 2x funds); Databento's price for all of them about US$0.01. The download goes ahead with a limit of US$1.
"""
if "### 3.113 Lag watch result" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.113 added")
else: print("  TRACK.md: 3.113 already there -- skipped")
