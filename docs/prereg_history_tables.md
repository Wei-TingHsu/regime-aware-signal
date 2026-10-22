# Pre-registration — history tables H0–H7 (TRACK §3.25)

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
| 2026-10-19 | **Second horizon and a lower floor.** Every table is tested at 5 sessions as well as 20; the frequency-gap floor is 10 points (was 15); with 6 tables × 6 markets × 2 horizons = 72 cells, a PASS now also needs p < 0.05 ÷ 6 = 0.0083 within its table. The 20-session results already recorded in §5 stand as written under the old rule; all cells are re-evaluated under the new rule and recorded again. | Founder's point: an event's effect can act over days and be swamped by other news within a month; and 15 points of frequency was stricter than a usable signal needs (60/40 is one). The tighter p guards against manufacturing passes by adding cells. **Prior #54 (Claude):** at 5 sessions Fed days show the largest gaps, but no cell clears 10 points at p < 0.0083 — everything FAIL or INCONCLUSIVE. |
| 2026-10-19 | **Second horizon and a lower floor.** Every table is tested at 5 sessions as well as 20; the frequency-gap floor is 10 points (was 15); with 6 tables × 6 markets × 2 horizons = 72 cells, a PASS now also needs p < 0.05 ÷ 6 = 0.0083 within its table. The 20-session results already recorded in §5 stand as written under the old rule; all cells are re-evaluated under the new rule and recorded again. | Founder's point: an event's effect can act over days and be swamped by other news within a month; and 15 points of frequency was stricter than a usable signal needs (60/40 is one). The tighter p guards against manufacturing passes by adding cells. **Prior #54 (Claude):** at 5 sessions Fed days show the largest gaps, but no cell clears 10 points at p < 0.0083 — everything FAIL or INCONCLUSIVE. |
| 2026-10-19 | **H3 threshold 3% → 2%** within five sessions, up and down. | Event count, not result: 3% produced 6 up / 3 down events since 1995 (a five-session 3% move in DXY is a ~3-sigma event); no test could run and no 2% result had been seen when this was written. Prior for 2% unchanged: FAIL on all six, gaps < 15 pts. |

## 5. Results

| date | table | result | prior |
|---|---|---|---|
| 2026-10-19 | H0 | Measured, no test (as registered). 20-session medians inside each label vs all history: SPY, TLT, UUP within 1 pt everywhere. Gold regime 3 **+2.4% vs +0.7%** (60 sessions +7.5% vs +2.4%; positive 68% vs 56%). WTI regime 1 +2.6%, regime 3 **−1.3%** vs +0.9%; USO regime 1 +2.0% vs +0.5%. Label −1 = sessions before the model had enough history to label. Session counts are overlapping windows (÷20 ≈ independent cases). `docs/history_H0.md`, `processed/history_tables.json`. | **#49 wrong**: gold and oil exceed 1 pt; TLT does not. Tally 49. |
| 2026-10-19 | H1 | 132 Fed decision days (2011 on — `fomc_decisions.csv` starts 2011, so ~250 was a wrong size guess, not a prior). Uniform test FAIL ×6; yield-up vs yield-down split FAIL ×6. Gold +0.7% / month, 53% positive vs 56% normally; split +0.2% vs +1.2%. `docs/history_H1.md` | **#50 right** |
| 2026-10-19 | H3 | 3% threshold: 6 up, 3 down events → INCONCLUSIVE everywhere. Amended to 2% (§4) and rerun same day; see next row. | **#51 wrong** (expected 60–80 events each way). Tally 50 |
| 2026-10-19 | H4 | 56 up / 60 down. Down: FAIL ×6; up: FAIL SPY, TLT, WTI_SPOT; GLD, UUP, USO INCONCLUSIVE (ETF histories start 2004–07; most up-shocks earlier). Measured: gold after a 25 bp+ **drop** +2.4% / month, +5.2% / quarter, 65% positive vs 56% (gap +9, FAIL). `docs/history_H4up.md`, `history_H4dn.md` | **#52 right** where testable |
| 2026-10-19 | H5 | 32 label changes (2008 on). FAIL ×6. Measured: USO +3.7% / month, 69% positive vs 52%, gap +16 pts, p 0.07 — met the gap, not the null. `docs/history_H5.md` | **#53 right** |
| 2026-10-19 | H3 (2%) | 21 up / 15 down events → still INCONCLUSIVE on every market (rule: 30). Not lowered again. Measured: after dollar jumps gold −1.4% / month (38% positive, n 21), oil −1.7%; after dollar drops gold +1.0%, oil +2.0% (USO) / +4.4% (spot), 60% positive. The dollar series' start date limits n — see CURRENT_STATE 18.31. `docs/history_H3up.md`, `history_H3dn.md` | amendment prior (FAIL) not scored: no verdict was produced |
| 2026-10-19 | H1–H5 under §4 amendment | Rerun at 5 and 20 sessions, gap floor 10 pts, p < 0.0083: **no PASS in any of the 72 cells**. H1 FAIL ×12 (both horizons, split), H4dn FAIL ×12, H5 FAIL ×12, H4up FAIL SPY/TLT/WTI ×2 + INCONCLUSIVE GLD/UUP/USO, H3 INCONCLUSIVE ×24 (21/15 events). All six event tables close as measured-only; they stay on the app with their tags. | **#54 right** |
