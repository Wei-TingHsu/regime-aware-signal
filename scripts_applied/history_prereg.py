"""19 Oct: register the history-table programme (H0–H7) before code. Writes docs/prereg_history_tables.md and TRACK §3.25.
Run from the repo root:  python history_prereg.py"""
from pathlib import Path
import sys

p = Path("docs/prereg_history_tables.md")
if p.exists(): print("  prereg_history_tables.md: already")
else:
    p.write_text(r"""# Pre-registration — history tables H0–H7 (TRACK §3.25)

*Registered 2026-10-19, before any code. Purpose: the app's "What history says" paragraph is fed today by one study (A3, oil shocks).
This programme adds conditional path tables for other recurring events and conditions, each a count of what happened — never a
forecast — plus one registered test per table for the only claim a table could support. Results appear in the app only with their
tag: the table as `measured`, the test as `tested: <verdict>`.*

## 1. Common engine (fixed)

- Markets: SPY, TLT, GLD, UUP, USO, WTI_SPOT (as A3). Sample 1995-01-03 → last complete session; ETF pre-inception = NaN (A3 rule).
- Event → forward log returns at 5, 10, 20, 40, 60 sessions; worst and best cumulative within 60 and their session; reported as
  simple % medians with inter-quartile range and n. A session is one trading day.
- Overlap: events within 20 sessions of a prior event collapse to the first (GAP = 20, as A3).
- Base rate: the market's unconditional 20-session sign share over the same sample (its drift), not 50%.
- Conditional test, identical for every table: the 20-session sign share after events differs from the base rate by ≥ 15 points,
  n ≥ 30, random-date null p < 0.05 (10,000 draws of n random non-event dates, same sample). PASS / FAIL / INCONCLUSIVE (n < 30).
  Where a table has a split (H1), the test is between the two halves of the split instead, same thresholds.
- Nothing is tuned: thresholds below are set here and do not move; any change is a dated amendment in §4 before rerun.

## 2. Tables

| id | event / condition | definition | source on disk | prior n | conditional test |
|---|---|---|---|---|---|
| H0 | today's regime | each market's 20-session return inside each regime label vs all history | regime label series (expanding labels, as the app's strip) | 4 labels, thousands of sessions each | **measured only** — no test; the label is the engine's own input, so testing it here would double-count T3 |
| H1 | Fed decision days | FOMC statement days; split by sign of the 2-yr yield change on the day (hawkish/dovish proxy) | FOMC calendar (event_calendar / release calendar) + FRED DGS2 | ~250 | split test: up-yield vs down-yield halves |
| H2 | jobs & CPI release days | Employment Situation and CPI release days; split by sign of print vs prior print (the 08:30 reader's naive surprise) | FRED release-date API ids 50 / 10 + series | ~300 each | split test — **deferred** until the 08:30 reader has one month live (consistency with its live reads) |
| H3 | dollar shocks | DXY (the series blindspot reads) ≥ +3% within 5 sessions; down-shocks ≤ −3% as a second table | blindspot dollar series | ~60–80 each | events vs base rate, up and down separately |
| H4 | rate shocks | 2-yr yield +25 bp / −25 bp within 5 sessions, separate tables | FRED DGS2 | ~120 total | events vs base rate, up and down separately |
| H5 | regime changes | first session of a new regime label | regime label series | ~40–60 | events vs base rate |
| H6 | equity drawdown entry | first session SPY closes ≥ 10% below its one-year high after ≥ 60 sessions above that line | SPY | ~25 | INCONCLUSIVE by construction (n < 30) — measured only until n allows |
| H7 | volatility spikes | VIX ≥ +30% within 5 sessions | FRED VIXCLS | ~70 | events vs base rate; feeds §3.24 |

Build order: H0, H1, H3, H4, H5 now (one module, `src/history_tables.py`, shared engine); H2 after the reader's first month; H6, H7 after.

## 3. Priors (Claude's, 2026-10-19, counted if wrong)

- #49 H0: no market's 20-session median inside any regime differs from its all-history median by more than 1 percentage point; gold and TLT
  show the widest spread. Table is useful for the app, carries no edge.
- #50 H1: gold's −0.3% two-session drift after statements (register cell) does not extend to 20 sessions; the hawkish/dovish split gap for
  every market is < 15 points → FAIL on all six.
- #51 H3: after dollar up-shocks gold's 20-session median is negative (≈ −1%) and USO's negative; sign-share gaps < 15 points → FAIL; the
  table is informative, the test is not.
- #52 H4: rate up-shocks: TLT 20-session median ≈ −1%, SPY flat; gaps < 15 points → FAIL both directions.
- #53 H5: regime changes: no market's gap ≥ 15 points → FAIL. (If this passes, the regime label alone has 20-session information the engine
  does not use; that would be the most important result of the programme.)

## 4. Amendments

| date | change | reason |
|---|---|---|
""")
    print("  prereg_history_tables.md: written")

t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.25 History tables" in s: print("  TRACK 3.25: already")
else:
    add = """### 3.25 History tables H0–H7 — conditional path tables for the app (registered 19 Oct, not built)

The Context block (§3.23) is fed by one study, oil shocks. This programme adds tables for Fed days (H1), jobs/CPI days (H2), dollar shocks
(H3), rate shocks (H4), regime changes (H5), equity drawdown entries (H6), volatility spikes (H7), and the current regime's own return
table (H0). One shared engine, one uniform test (20-session sign share vs the market's base rate, ≥ 15 points, n ≥ 30, random-date null
p < 0.05), priors #49–#53. Tables enter the app as `measured`; tests as `tested: <verdict>`. `docs/prereg_history_tables.md`.
Build order H0, H1, H3, H4, H5; H2 after the 08:30 reader's first month; H6, H7 after.

"""
    anchor = "## 4. Potential upgrades — not registered, not costed\n"
    if anchor not in s: sys.exit("  TRACK anchor not found -- stopped")
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.25: done")
print("done")
