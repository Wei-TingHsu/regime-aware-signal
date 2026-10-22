"""19 Oct: repair the live document feed (TRACK 3.26).
  fetch_sources political --out <dir>   (new flag; default unchanged)
  daily_run.sh step 3: + 8-K fetch (edgar, --limit 6 per ticker, skips existing), + executive orders -> political_order/, + proclamations/memoranda/
  determinations -> political_other/.  Step 4 reads them under the existing 40-per-source cap; step 6 already reads those two sources.
  Also: src/context.py `show` date parsing.  Run from the repo root:  python feed_setup.py"""
from pathlib import Path
import sys

# ---- fetch_sources: --out for political
p = Path("src/fetch_sources.py"); s = p.read_text()
if '"--out"' in s and 'args.out' in s: print("  fetch_sources --out: already")
else:
    old1 = '    out = DOCS / "political"; out.mkdir(parents=True, exist_ok=True)\n    want = {t.strip().lower() for t in args.types.split(",") if t.strip()}'
    new1 = '    out = DOCS / args.out; out.mkdir(parents=True, exist_ok=True)\n    want = {t.strip().lower() for t in args.types.split(",") if t.strip()}'
    old2 = '    p.add_argument("--start", default="2011-01-01")'
    new2 = '    p.add_argument("--out", default="political", help="folder under data_provenance/docs; the report reads political_order and political_other")\n    p.add_argument("--start", default="2011-01-01")'
    if old1 not in s or old2 not in s: sys.exit("  fetch_sources anchors not found -- stopped")
    p.write_text(s.replace(old1, new1, 1).replace(old2, new2, 1)); print("  fetch_sources --out: added")

# ---- daily_run.sh step 3
d = Path("daily_run.sh"); s = d.read_text()
if "fetch_sources edgar" in s: print("  daily_run step 3: already")
else:
    anchor = '  || echo "  fetch failed -- continuing, the corpus is additive"\n'
    if anchor not in s: sys.exit("  daily_run anchor not found -- stopped")
    add = '''# 19 Oct (TRACK 3.26): the live feed had two routing faults -- no nightly 8-K fetch since the backfill (last earnings document 14 Aug),
# and presidential documents landing in political/ which step 6 never reads. Earnings: SEC submissions feed, free, skips files on disk.
# Executive orders -> political_order/, proclamations/memoranda/determinations -> political_other/ (the two folders step 6 reads).
SINCE14="$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)"
python -m src.fetch_sources edgar --limit 6 || echo "  8-K fetch failed -- continuing, the corpus is additive"
python -m src.fetch_sources political --start "$SINCE14" --limit 100000 --max-pages 3 --types "executive order" --out political_order \\
  || echo "  executive-order fetch failed -- continuing"
python -m src.fetch_sources political --start "$SINCE14" --limit 100000 --max-pages 3 --types "proclamation,memorandum,determination,presidential order" --out political_other \\
  || echo "  proclamation fetch failed -- continuing"
'''
    d.write_text(s.replace(anchor, anchor + add, 1)); print("  daily_run step 3: 8-K + routed political fetches added")

# ---- context.py show date
c = Path("src/context.py"); s = c.read_text()
old = '        day = a.day or sorted(glob.glob("outputs/reports/*.json"))[-1].split("/")[-1][:10]'
if old in s:
    s = s.replace(old, '        _st = Path(sorted(glob.glob("outputs/reports/*.json"))[-1]).stem\n        day = a.day or f"{_st[:4]}-{_st[4:6]}-{_st[6:8]}"', 1)
    c.write_text(s); print("  context show date: fixed")
else: print("  context show date: already/absent")

# ---- TRACK 3.26 + CURRENT_STATE 18.32
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.26 Live document feed" in s: print("  TRACK 3.26: already")
else:
    add = """### 3.26 Live document feed repaired (19 Oct)

Found while building §3.23: 29 of the last 30 report days carried zero documents. Two routing faults, not the engine: (1) no nightly 8-K
fetch existed — the earnings source, the only one scoring above chance in the backfill (62%), last received a document on 14 Aug 2026;
(2) `fetch_sources political` wrote every presidential document to `political/`, a folder step 6 never reads; the report reads
`political_order/` and `political_other/`, last filled 14 Aug. Fix: `--out` on the political fetch; nightly step 3 now fetches 8-Ks
(SEC submissions feed, 9 registered tickers, skips files on disk) and routes executive orders / proclamations to the two read folders.
Reading stays under step 4's 40-per-source cap. **Reports for 15 Aug – 19 Oct keep their as-of state** (zero documents): regenerating them
with documents read later would make the record look better than the engine was on the day. Forward from 20 Oct the feed is live.
Also noted: the 16 Oct run died inside step 2 with no error text and 17 Oct never ran (scheduler outside the repo); `daily_run.sh` has no
git step, so the cloud app shows the last manual push.

"""
    anchor = "## 4. Potential upgrades — not registered, not costed\n"
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.26: done")

cs = Path("docs/CURRENT_STATE_2026-08-23.md"); s = cs.read_text()
if "### 18.32" in s: print("  CURRENT_STATE 18.32: already")
else:
    cs.write_text(s.rstrip("\n") + """

### 18.32 Live feed repaired (19 Oct)

Earnings 8-Ks were never fetched nightly (last document 14 Aug); presidential documents were fetched into a folder the report does not read.
Both routes fixed in `daily_run.sh` step 3 (TRACK 3.26). Past reports are not regenerated — the zero-document stretch 15 Aug – 19 Oct is
recorded as a feed outage, not as engine abstention. Scoreboard cells counted over live days should be read with that gap in mind.
"""); print("  CURRENT_STATE 18.32: appended")
print("done")
