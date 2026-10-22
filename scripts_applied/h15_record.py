"""19 Oct: record H1/H3/H4/H5 (priors #50 right, #51 wrong -> tally 50, #52 right where testable, #53 right); amend H3 threshold 3% -> 2%
(reason: 6 / 3 events); Context block renders each table as its own paragraph. Run from the repo root:
  python h15_record.py ; python -m src.history_tables h3 2>&1 | tail -4 ; python -m src.context show GLD | sed -n 5,12p"""
from pathlib import Path
import sys

# ---- prereg §4 amendment + §5 results
p = Path("docs/prereg_history_tables.md"); s = p.read_text()
if "H3 threshold 3% → 2%" in s: print("  prereg H3 amendment: already")
else:
    old = "| date | change | reason |\n|---|---|---|\n"
    if old not in s: sys.exit("  prereg §4 anchor not found")
    s = s.replace(old, old + "| 2026-10-19 | **H3 threshold 3% → 2%** within five sessions, up and down. | Event count, not result: 3% produced 6 up / 3 down events since 1995 "
                  "(a five-session 3% move in DXY is a ~3-sigma event); no test could run and no 2% result had been seen when this was written. Prior for 2% unchanged: FAIL on all six, gaps < 15 pts. |\n", 1)
    print("  prereg H3 amendment: added")
if "| 2026-10-19 | H1 |" in s: print("  prereg §5 H1–H5: already")
else:
    s = s.rstrip("\n") + """
| 2026-10-19 | H1 | 132 Fed decision days (2011 on — `fomc_decisions.csv` starts 2011, so ~250 was a wrong size guess, not a prior). Uniform test FAIL ×6; yield-up vs yield-down split FAIL ×6. Gold +0.7% / month, 53% positive vs 56% normally; split +0.2% vs +1.2%. `docs/history_H1.md` | **#50 right** |
| 2026-10-19 | H3 | 3% threshold: 6 up, 3 down events → INCONCLUSIVE everywhere. Amended to 2% (§4) and rerun same day; see next row. | **#51 wrong** (expected 60–80 events each way). Tally 50 |
| 2026-10-19 | H4 | 56 up / 60 down. Down: FAIL ×6; up: FAIL SPY, TLT, WTI_SPOT; GLD, UUP, USO INCONCLUSIVE (ETF histories start 2004–07; most up-shocks earlier). Measured: gold after a 25 bp+ **drop** +2.4% / month, +5.2% / quarter, 65% positive vs 56% (gap +9, FAIL). `docs/history_H4up.md`, `history_H4dn.md` | **#52 right** where testable |
| 2026-10-19 | H5 | 32 label changes (2008 on). FAIL ×6. Measured: USO +3.7% / month, 69% positive vs 52%, gap +16 pts, p 0.07 — met the gap, not the null. `docs/history_H5.md` | **#53 right** |
"""
    print("  prereg §5 H1–H5: appended")
p.write_text(s)

# ---- TRACK
t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "In the app as `measured` under \"What history says in today's condition\". H1, H3, H4, H5 next.\n"
if "H1/H4/H5 run 19 Oct" in s: print("  TRACK 3.25 results: already")
elif anchor not in s: print("  TRACK 3.25 anchor not found -- add by hand")
else:
    t.write_text(s.replace(anchor, anchor + "**H1/H4/H5 run 19 Oct:** every testable cell FAIL (H1 132 days, H4 56/60 shocks, H5 32 changes); H3 at 3% gave 6/3 events (#51 wrong, "
                 "tally 50) → amended to 2% before rerun. Measured and on the page: gold +2.4%/month after 25 bp+ yield drops (65% vs 56%); oil +3.7%/month after a "
                 "label change (69% vs 52%, p 0.07). H2 waits for the reader's first month; H6, H7 after. Open: gold/dollar/oil cells in H4up need pre-ETF spot series.\n", 1))
    print("  TRACK 3.25 results: done")

# ---- MASTER
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 50" in s: print("  MASTER tally: already")
else:
    old = "#49 H0 regime spread, all Claude's)"
    if old in s: s = s.replace(old, "#49 H0 regime spread, #51 H3 dollar-shock count, all Claude's)", 1).replace("tally 49 (#40", "tally 50 (#40", 1)
    else: print("  MASTER tally anchor not found -- edit by hand: tally 49 -> 50 (#51 H3 count)")
    s = s.replace("| H0 measured 19 Oct: gold regime 3 +2.4% vs +0.7% (#49 wrong); priors #50–#53 open |",
                  "| H0 measured; H1, H4, H5 FAIL on every testable cell (#50, #52, #53 right); H3 at 3% gave 6/3 events (#51 wrong), amended to 2% |", 1)
    m.write_text(s); print("  MASTER tally 50 + row 45: done")

# ---- CURRENT_STATE
c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "H1, H3, H4, H5 ran the same day" in s: print("  CURRENT_STATE: already")
else:
    anchor = "recorded as a feed outage, not as engine abstention. Scoreboard cells counted over live days should be read with that gap in mind.\n"
    if anchor not in s: print("  CURRENT_STATE 18.32 anchor not found -- add by hand")
    else:
        c.write_text(s.replace(anchor, anchor + "\n**H1, H3, H4, H5 ran the same day** (18.31 cont.): every cell that could be tested failed the uniform test — Fed days (132), "
                     "rate shocks (56 up / 60 down), regime changes (32). The dollar table at 3% produced 6 / 3 events (prior #51 wrong on size, tally 50); "
                     "amended to 2% before any rerun. Measured rows worth reading on the page: gold +2.4% / month after 25 bp+ yield drops (65% positive vs 56%), "
                     "oil +3.7% / month after a label change (69% vs 52%, p 0.07). All on the app under \"What history says after shocks and events\", each with its tag.\n", 1))
        print("  CURRENT_STATE: H1–H5 added")

# ---- H3 threshold 2%
h = Path("src/history_tables.py"); s = h.read_text()
if "np.log(1.02)" in s: print("  H3 threshold: already 2%")
else:
    s = s.replace("x5 = dxy_r.rolling(5).sum(); thr = np.log(1.03)", "x5 = dxy_r.rolling(5).sum(); thr = np.log(1.02)  # amended 19 Oct from 3%: 6/3 events; prereg §4", 1)
    s = s.replace('"Dollar jumps: DXY ≥ +3% within five sessions"', '"Dollar jumps: DXY ≥ +2% within five sessions (amended from 3%, prereg §4)"', 1)
    s = s.replace('"Dollar drops: DXY ≤ −3% within five sessions"', '"Dollar drops: DXY ≤ −2% within five sessions (amended from 3%, prereg §4)"', 1)
    h.write_text(s); print("  H3 threshold: 2%")

# ---- context: one paragraph per table, H3 lead text
q = Path("src/context.py"); s = q.read_text()
s = s.replace('("H3up", "After dollar jumps (≥ 3% in five sessions)"), ("H3dn", "After dollar drops (≥ 3% in five sessions)")',
              '("H3up", "After dollar jumps (≥ 2% in five sessions)"), ("H3dn", "After dollar drops (≥ 2% in five sessions)")', 1)
old = '    if s2: P.append(("What history says after shocks and events, and the engine\'s record", " ".join(s2)))'
if old in s:
    s = s.replace(old, '    if s2: P.append(("What history says after shocks and events, and the engine\'s record", \'</p><p class="rs-ctx-p">\'.join(s2)))', 1)
    print("  context: one paragraph per table")
else: print("  context paragraph anchor: already/absent")
q.write_text(s)
print("done -- python -m src.history_tables h3 2>&1 | tail -4")
