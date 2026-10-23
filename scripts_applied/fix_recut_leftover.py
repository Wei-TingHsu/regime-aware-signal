"""Hotfix: remove the withdrawn re-cut branch in why_moved.run() (it expected zigzag-style cells); record #75. Run from the repo root: python scripts_applied/fix_recut_leftover.py"""
from pathlib import Path
import ast
wm = Path("src/why_moved.py"); s = wm.read_text()
a = s.find('            if (bb["mult"], bb["floor"]) != (MULT, FLOOR):')
b = s.find('            cvb = attr_curve(r, F, s0b, max_k=MAX_K, window=bb["window"])')
if a > 0 and b > a:
    s = s[:a] + "            s0b, db, Lb = s0, direction, Lnow        # no re-cut (founder, 23 Oct): the cell was swept on the legs the page shows\n" + s[b:]
    print("  re-cut branch removed")
else: print("  re-cut branch: already absent")
old = '                ib0, ib1, _ = impulse_window(r, s0b, db, float(max(bb["floor"], bb["mult"] * r.rolling(20).std().iloc[-1] * np.sqrt(20))))'
if old in s: s = s.replace(old, '                ib0, ib1, _ = impulse_window(r, s0b, db, float(thr[s0_pos]))', 1); print("  impulse threshold: from the leg's own threshold")
wm.write_text(s); ast.parse(s); print("  why_moved parses")
p = Path("docs/prereg_factor_attribution.md"); t = p.read_text()
if "| 2026-10-23 | T-G on the current-leg rule |" not in t:
    p.write_text(t.rstrip("\n") + "\n| 2026-10-23 | T-G on the current-leg rule (GLD) | 72 cells on the two-step rule's legs: best 79% at look-back 252; patience flat from 7 to 30 (all 79%), min window 3 or 5 alike; beats the full leg in 86–97% of legs; survives the sweep null. The page quotes this cell for these legs. | **#75 right** |\n"); print("  prereg: #75 recorded")
