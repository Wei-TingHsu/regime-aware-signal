"""record_26nov_cds2_registered.py -- TRACK 3.130: the gold leg of the 25 Nov turn; the founder's two YES; test CDS-2 (inside the day) registered BEFORE it runs. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.130 The turn of 25 Nov with gold; daily CDS collection; test CDS-2 registered (26 Nov 12:30)
**The turn of 25 Nov, all four futures (most-traded contracts; founder's run of 26 Nov 10:36; moves from 08:29 New York).**
| | 09:30 | 09:45 | 10:00 | 10:30 | 10:45 | 11:00 | 11:10 | 11:20 | 11:30 | 12:00 | 12:59 | low of the morning | inside 10:30-12:00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S&P 500 | -0.43% | -1.22% | -0.46% | -0.85% | -1.08% | -0.85% | -1.06% | -1.00% | -0.84% | -0.59% | +0.75% | 09:45, -1.44% | low 11:17 |
| Nasdaq-100 | -0.74% | -1.77% | -0.68% | -1.48% | -1.83% | -1.56% | -1.88% | -1.73% | -1.56% | -1.15% | +0.50% | 09:45, -2.11% | low 11:17 |
| gold | -1.17% | -1.16% | -1.06% | -1.87% | -1.87% | -1.66% | -1.57% | -1.50% | -1.24% | -1.08% | +0.27% | 10:19, -2.26% | low 10:30 |
| 10-year note (price) | +0.12% | +0.17% | +0.07% | +0.15% | +0.16% | +0.22% | +0.22% | +0.16% | +0.15% | +0.15% | +0.01% | 08:30 | HIGH 11:01 |
**What it says.** The three markets did not turn at one minute. Gold made its low at 10:19 and climbed from about 10:45; shares made a second low at 11:17 (the first was 09:45) and climbed from there; the 10-year note's price peaked at 11:01 and then fell back. In the founder's words they 'bounced back' -- true for shares and gold, an hour apart; bonds went the other way from 11:00. Gold fell 2.26% while bond yields FELL after the release, so gold's fall was not a 'hawkish data' move either. Cause of the turns: not established (3.129).
**Founder, 26 Nov 10:36: 'yes for both'** -- (1) the CDS question inside the day; (2) keep collecting the public CDS files every day.
**(2) Daily collection.** `python -m src.cds_public fetch` asks only for the days not yet on disk; it joins the daily block. Own testing only (3.127).
**(1) Test CDS-2 (`python -m src.cds_intraday run`), registered before it runs.**
- Events: trades of the 5-year CDS of a company whose spread is GIVEN in the file (the worked-out spreads are too noisy at the edge, 3.129), compared with that company's previous such trade at least one minute earlier and at most 5 days back; the event's size = the change of the spread; wider = credit worse. Trades from one minute after the 09:30 open to the close, New York.
- Two sets of events: the five AI spenders with a share in the pool (Oracle, Amazon, Meta, Microsoft, Alphabet), and Oracle alone. Two shares measured: the company's own share, and the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM, the average of their moves). Two thresholds for the size of the change: 1% and 5%. Four look-aheads: 5, 15, 30, 60 minutes, from the first full minute after the trade, inside the session.
- Measure: the average of (direction of the spread change) x (share move). Negative = shares fall after a widening and rise after a tightening: the CDS trade came first. Beside it, the same over the minutes BEFORE the trade (the other way round: shares first).
- Chance: 5,000 copies in which each event day is moved to another session within 20 sessions (all events of a day together, same minute of the day). 2 x 2 x 2 x 4 = 32 tests; limit 0.05 / 32 = 0.0016. Under 30 events: too few to judge. Result: `docs/cds_intraday.md`.
- Checked on made-up data before sending: a planted fall of 8 basis points after Oracle widenings was found (-5 to -10 basis points at the smallest chance the copies allow); events without a planted effect showed nothing.
**What a pass would not mean (stated first).** The time in the file is when the trade was DONE. The SEC's rule lets a trade be reported up to a day later, and the files do not say when each one became public. A pass = 'the CDS market moved first'; whether it could have been SEEN in time needs the live files watched through the day -- not built.
**Priors.** #232: no test passes. #233: the 'before' numbers are negative and larger than the 'after' numbers for the own share at 60 minutes (shares move first, the CDS trade follows). #234: fewer than 300 events of the five AI spenders at the 5% threshold.
"""
if "### 3.130 The turn of 25 Nov with gold" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.130 added")
else: print("  TRACK.md: 3.130 already there -- skipped")
