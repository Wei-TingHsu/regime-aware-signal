"""19 Oct: record H3 at 2% (INCONCLUSIVE: 21 up / 15 down) and print the dollar series' first date. Run from the repo root: python record_h3.py"""
from pathlib import Path
import sys
p = Path("docs/prereg_history_tables.md"); s = p.read_text()
if "| 2026-10-19 | H3 (2%) |" in s: print("  prereg H3 2%: already")
else:
    p.write_text(s.rstrip("\n") + "\n| 2026-10-19 | H3 (2%) | 21 up / 15 down events → still INCONCLUSIVE on every market (rule: 30). Not lowered again. Measured: after dollar jumps gold "
        "−1.4% / month (38% positive, n 21), oil −1.7%; after dollar drops gold +1.0%, oil +2.0% (USO) / +4.4% (spot), 60% positive. The dollar series' start date limits n — "
        "see CURRENT_STATE 18.31. `docs/history_H3up.md`, `history_H3dn.md` | amendment prior (FAIL) not scored: no verdict was produced |\n")
    print("  prereg H3 2%: appended")
t = Path("docs/TRACK.md"); s = t.read_text()
old = "Open: gold/dollar/oil cells in H4up need pre-ETF spot series.\n"
if "H3 at 2%: 21/15" in s: print("  TRACK: already")
elif old in s:
    t.write_text(s.replace(old, "H3 at 2%: 21/15 events, INCONCLUSIVE, not lowered again. Open: gold/dollar/oil cells in H4up need pre-ETF spot series; H3 needs a dollar series "
                 "that starts before the one the engine reads.\n", 1)); print("  TRACK: H3 2% noted")
else: print("  TRACK anchor not found -- add by hand")
c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
old = "each with its tag.\n"
if "H3 rerun at 2%" in s: print("  CURRENT_STATE: already")
elif old in s:
    c.write_text(s.replace(old, old + "H3 rerun at 2%: 21 up / 15 down — INCONCLUSIVE everywhere; the measured directions are the textbook ones (gold down after dollar jumps, "
                 "oil up after dollar drops) and too few to test. Not lowered again.\n", 1)); print("  CURRENT_STATE: H3 noted")
else: print("  CURRENT_STATE anchor not found -- add by hand")
try:
    sys.path.insert(0, "."); import pandas as pd
    from src.oil_shock import load
    rets, dgs2, dxy = load(); dxy = pd.Series(dxy).dropna(); dgs2 = pd.Series(dgs2).dropna()
    print(f"  dollar series: {dxy.index[0].date()} -> {dxy.index[-1].date()} ({len(dxy):,} sessions); 2-yr: {dgs2.index[0].date()} -> {dgs2.index[-1].date()}")
except Exception as e: print(f"  series check skipped: {type(e).__name__}: {e}")
print("done")
