"""
E4 — event-bin alignment lever. Registered: docs/prereg_asymmetry_levers.md §2. Run from the repo root.

Adds to step6_report.py, switched by LEVER=E4 in the environment (default off -> incumbent untouched):
  a document counts toward a market's net view only if, among its source class's precedents on that asset through
  t-1 (expanding), the move in the document's own bin had the sign of the reading at least as often as the other bin
  did. Fewer than 30 precedents -> aligned (no evidence to exclude).
Bins: FOMC statement/minutes -> intraday (open->close); everything else -> overnight (prev close -> open).
Needs processed/ohlc_core.parquet (src.attribution --build-ohlc).

Then: LEVER=E4 python -m src.report_backfill --hash 48a6c4e879a1_n2617_h2_E4 --n-perm 10000
"""
from pathlib import Path

p = Path("step6_report.py"); s = p.read_text()
if "LEVER_E4" in s:
    print("already patched"); raise SystemExit

helper = '''
# ---- E4 lever (docs/prereg_asymmetry_levers.md §2), off unless LEVER=E4 ----------------------------------
import os as _os
LEVER_E4 = _os.environ.get("LEVER", "") == "E4"
_E4_BIN = {"fomc_statement": "intraday", "fomc_minutes": "intraday"}       # all other classes: overnight
_E4_OHLC = None
_E4_CACHE = {}


def _e4_bins(asset):
    global _E4_OHLC
    if _E4_OHLC is None:
        _E4_OHLC = pd.read_parquet("processed/ohlc_core.parquet")
    o, c = _E4_OHLC[(asset, "Open")], _E4_OHLC[(asset, "Close")]
    return pd.DataFrame({"overnight": np.log(o / c.shift(1)), "intraday": np.log(c / o)})


def e4_aligned(source, asset, axcol, hist, t):
    """True if this source class, on its precedents for `asset` before t, moved its own bin with the reading
    at least as often as the other bin. Expanding, through the precedents already in `hist` (<= t - PRIMARY_H)."""
    key = (source, asset, t)
    if key in _E4_CACHE: return _E4_CACHE[key]
    bins = _e4_bins(asset); own = _E4_BIN.get(source, "overnight"); other = "intraday" if own == "overnight" else "overnight"
    h = hist[hist.source == source]
    d = pd.to_numeric(h[axcol], errors="coerce")
    h = h.assign(dir=d)[d.abs() > NEGLIGIBLE]
    if len(h) < 30:
        _E4_CACHE[key] = True; return True
    b = bins.reindex(pd.DatetimeIndex(h.session.values))
    own_hits = (np.sign(b[own].values) == np.sign(h["dir"].values)).mean()
    other_hits = (np.sign(b[other].values) == np.sign(h["dir"].values)).mean()
    ok = bool(np.nan_to_num(own_hits) >= np.nan_to_num(other_hits))
    _E4_CACHE[key] = ok; return ok
'''
# insert the helper after PRIMARY_H definition line
k = s.index("NEGLIGIBLE, PRIMARY_H, CONF_WARN")
eol = s.index("\n", k) + 1
s = s[:eol] + helper + s[eol:]

old = '        live = td[td["dir"].abs() > NEGLIGIBLE]\n        entry["n_docs_today"] = int(len(live))'
new = '''        live = td[td["dir"].abs() > NEGLIGIBLE]
        if LEVER_E4 and len(live):
            keep = [e4_aligned(str(r.source), asset, axcol, hist, t) for r in live.itertuples()]
            dropped = int(len(live) - sum(keep))
            live = live[keep]
            if dropped:
                entry["e4_dropped"] = dropped
        entry["n_docs_today"] = int(len(live))'''
assert s.count(old) == 1, "net-view anchor not found"
s = s.replace(old, new)
p.write_text(s); print("step6_report.py: E4 lever added (off by default; LEVER=E4 to enable)")

# the backfill must write to a distinct tag and the lever must be visible in the report
b = Path("src/report_backfill.py"); t = b.read_text()
if 'R["lever"]' not in t:
    t = t.replace('        R["estimate_horizon_sessions"] = s6.PRIMARY_H', '        R["estimate_horizon_sessions"] = s6.PRIMARY_H\n        R["lever"] = os.environ.get("LEVER", "")', 1)
    if "import os" not in t: t = t.replace("import argparse", "import argparse\nimport os", 1)
    b.write_text(t); print("report_backfill.py: report carries the lever tag")
