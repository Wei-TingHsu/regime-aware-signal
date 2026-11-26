"""record_26nov_cds1_result_and_turn.py -- TRACK 3.129: the result of CDS-1 (priors #229-#231 scored); the minute prices of the 25 Nov turn. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.129 CDS-1: result (a null); the minute prices of the turn of 25 Nov (26 Nov 11:40)
**CDS-1, result (commit 661e213; `docs/leading_cds.md`).** 39,478 usable trades of 5-year single-company CDS (19,673 with the spread given, 19,805 worked out), 425 companies; 74 other companies form the market-wide move (460 days). **Only Oracle reaches 250 days with a spread (266 of 583; from 25 Feb 2025); the combined 'AI debt' series has 280 days.** Amazon 147, Meta 108, Intel 103, IBM 95, Microsoft 90, Alphabet 83, AMD 74, Nvidia 69, CoreWeave 2: not tested.
**2 candidates x 4 = 8 tests, limit: chance under 0.00625. 0 of 2 pass.** Oracle's CDS spread: links -0.049 to -0.005, chance 0.38 to 0.97. 'AI debt': -0.071 to -0.010, chance 0.50 to 0.85. The other way round (chip shares first): +0.038 to -0.064, chance 0.56 to 0.97 -- nothing either. All tested days fall in ONE market condition, 'Rapid money growth, a high policy rate' (365 and 330 days); the other three had no days, as said before the run.
**Reading.** No sign that Oracle's CDS spread, or the AI borrowers' together, moves before semiconductor shares from one day to the next -- and none that shares move before the CDS. With 266 days a link would have to be about 0.17 or stronger to pass; a weaker one cannot be seen. 'Not found on 266 days in one market condition', not 'disproved'.
**What the data shows without a test (description).** Oracle's spread: about 38 basis points in its first 20 days with trades (from Feb 2025), about 298 in its last 20 (Nov 2026) -- nearly eight times wider. Amazon 26 -> 95, AMD 46 -> 136, Nvidia 71 -> 133, Meta 70 -> 114, Alphabet 52 -> 85, Microsoft 38 -> 53. The cost of insuring the debt of every large AI spender rose over the period; the founder's 'AI debt concern in the industry' is visible as a LEVEL. The test asked something narrower: whether the day-to-day changes come first.
**Check of the working-out (step 2 of 3.128).** On 248 company-days with both kinds of trade the worked-out spread differs from the given one by 4.2% in the middle and by 25.9% at the 9-in-10 mark: usable in the middle, noisy at the edge (older trades of the day, other maturities inside the 4.25-5.75 year band, payments that include accrued interest). A weakness of the series, recorded.
**Priors.** #229: first half RIGHT (no CDS series leads), second half WRONG (the other way round is not stronger; neither direction shows anything). #230 (at most 4 companies reach 250 days): RIGHT, one does. #231 (worked-out within 5% of given in the middle): RIGHT at 4.2%, with a wide tail.
**Not yet done from the outline of 3.127:** the same question INSIDE the day (the trade times against the 1-minute prices of the pool stocks). Registered when written.

**The turn of 25 Nov in 1-minute futures prices (`reversal_check prices`, founder's run of 26 Nov 10:11; moves from 08:29 New York, one minute before the release).**
| | 09:30 | 09:45 | 10:30 | 10:45 | 11:00 | 11:15 | 11:30 | 12:00 | 12:59 |
|---|---|---|---|---|---|---|---|---|---|
| S&P 500 futures | -0.43% | low -1.44% | -0.85% | -1.08% | -0.85% | -1.10% | -0.84% | -0.59% | +0.75% |
| Nasdaq-100 futures | -0.74% | low -2.11% | -1.48% | -1.83% | -1.56% | -1.87% | -1.56% | -1.15% | +0.50% |
| 10-year note futures (price) | +0.12% | | +0.15% | +0.16% | +0.22% | +0.20% | +0.15% | +0.15% | +0.01% |
**What it says.** (1) Shares made their low at 09:45, fell back to almost the same level at about 11:15 (S&P -1.10%, Nasdaq -1.87%) and rose from there without a break: the turn the founder saw at about 11:00 is that second low, at about 11:15. (2) Bonds did the opposite at that time: the 10-year note's price was UP after the release (yields fell -- the bond market did not trade the PCE figure as hawkish), reached its high at 11:01 and then gave everything back by 13:00. So from about 11:00-11:15 money left bonds while shares rose: not 'all markets bounced together', but shares up and bonds down. (3) Gold: no prices -- Claude's script asked for the nearest-expiry gold contract, which hardly trades (the lesson was already in `src/intraday_fetch.py`); fixed to the most-traded contract of each future, to be run again.
**Timed official items near it (3.128):** two Federal Register filings at 11:15 (not market news), the 7-year auction result at 11:33. European share markets close at 11:30 New York. None is shown to be the cause.
"""
if "### 3.129 CDS-1: result" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.129 added")
else: print("  TRACK.md: 3.129 already there -- skipped")
