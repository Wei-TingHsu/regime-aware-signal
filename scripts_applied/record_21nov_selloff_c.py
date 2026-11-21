"""record_21nov_selloff_c.py -- TRACK 3.95: sell-off stage C results (founder's definitions), priors #186-#189 scored; stage C2 registered BEFORE
running (is the price higher after h sessions?), priors #190-#192. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.95 Sell-off stage C results: with the founder's definitions the conditions do not predict; stage C2 registered (21 Nov 21:15)
`docs/selloff_model.md` (commit c533646). 16 tests, bar p < 0.0031, unit of evidence = the calendar month.
**Result: in none of the 16 tests is the model better than always quoting history; in 15 of 16 it is slightly worse (skill -0.2% to -5.7%; the sixteenth is +0.0%).**
| sell-off | REBOUND happened | skill | where the model said 10+ points above history | FURTHER SLIDE happened | skill | where it said 10+ points above |
|---|---|---|---|---|---|---|
| stocks, one day -5% | 23% | -0.9% | said 34%, history 21%, happened 18% (25 months) | 26% | -0.2% | said 38%, history 26%, happened 33% (70 months) |
| stocks, one day -7% | 23% | -1.6% | 35% / 21% / 19% | 27% | -1.1% | 40% / 27% / 26% |
| stocks, one day -10% | 21% | -2.6% | 33% / 19% / 22% | 30% | -5.7% | 42% / 28% / 19% |
| stocks, 5 sessions -10% | 22% | -1.7% | 37% / 22% / 19% | 25% | -1.6% | 36% / 23% / 26% |
| stocks, 10 sessions -15% | 26% | -1.8% | 33% / 21% / 11% (10 months) | 27% | -2.6% | 41% / 28% / 17% (9 months) |
| funds, one day -3% | 24% | -2.3% | 38% / 23% / 27% | 23% | -0.7% | 34% / 22% / 38% (19 months) |
| funds, one day -4% | 24% | -4.2% | 44% / 25% / 23% | 23% | -0.8% | 36% / 22% / 30% (18 months) |
| funds, 5 sessions -7% | 27% | -3.7% | 42% / 27% / 22% | 23% | +0.0% | 33% / 19% / 46% (7 months) |
**Reading.** After a big sell-off, two up-days in a row follow about 21-27% of the time and two down-days about 23-30% -- what two coin tosses give (25% each) -- and the twelve conditions known at the close do not move those odds in a way that holds in later years. When the model was most confident of a rebound, the rebound came LESS often than history in six of eight definitions. So for these two-session definitions the honest statement to an investor is the plain frequency, not a tailored probability.
**Priors.** #186 HALF: REBOUND 21-27% (inside 22-30% but for one definition at 21%); FURTHER SLIDE 23-30% (the upper part is outside 18-26%). #187 WRONG: for single stocks the skill is negative, not small and positive. #188 RIGHT. #189 RIGHT: nothing is usable.
**Why stage B looked more promising, and what follows.** Stage B measured the size of the PRICE move over five sessions and found repeating groups (results-day falls slide on; falls deep into a decline rebound) and a straight-line model with out-of-sample correlation 0.12-0.14 for one-day stock sell-offs. The colour of two daily candles is a different, noisier target: it ignores the overnight gap and looks only two sessions ahead. The founder's own short-window rule says to test different session lengths before concluding.
**Stage C2, registered now (`python -m src.selloff_model run2`).** Same events, conditions, year-by-year training on earlier years only, same check and the same unit of evidence (calendar month). Outcome changed to: **the close of session +h is above the sell-off day's close**, for each of the founder's horizons 1, 2, 3, 5, 7, 10 on its own ('price'); and for stocks also **the stock did better than the S&P 500 over those sessions**. 8 definitions x 6 horizons, twice for the five stock definitions: 78 tests; skill counts at p < 0.00064. 'Usable' as in 3.94, in either direction (the model says 10 or more points above history and it happens 5 or more points more often, or 10 below and 5 less often; 20 or more separate months). This is a further look at the same events; the bar is divided accordingly and the count of tests under 0.05 is reported against the number expected by luck (about 4).
**Priors.** #190: stocks, one day -5%, against the S&P 500, 5 sessions: skill above zero with p under 0.05, but not under 0.00064. #191: nothing is usable. #192: for the funds the number of tests under 0.05 is no more than luck gives.
"""
if "### 3.95 Sell-off stage C results" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.95 added")
else: print("  TRACK.md: 3.95 already there -- skipped")
