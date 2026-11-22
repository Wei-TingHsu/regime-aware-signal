"""record_22nov_selloff_search.py -- TRACK 3.99: first night run of the machine pattern search, three faults, and the corrected scrambling
registered BEFORE the re-run. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.99 Sell-off stage D, first night run: nothing beats scrambled data -- but the scrambling was too harsh; corrected and re-run (22 Nov 17:30)
`docs/selloff_search.md` (commit 489f90f, made on the founder's laptop; its push failed for lack of network and goes out with the next push). Downloads: Yahoo 20 series; SEC financials and industry codes for 104 companies; the SEC's insider data sets, 81 quarters; FINRA's daily short-sale files, 4,354 of 4,515 days back to 2010. **All nine FRED series failed** (connection dropped or timed out), so T4 ran without the credit spread, yield curve, stress and uncertainty indexes. Tables: T1 20,776 rows; T2 15,886; T3 15,886 (complete from 2010); T4 19 columns; T5; T6 2,397 rows (204 complete); T7 9,549 (from 2011); T8 15,684 (from 2006). The search took 0.96 hours with 300 scrambled repeats.
**First-run result (bar p < 0.0125).**
| group of sell-offs | pattern-outcome pairs tried | CONFIRMED on real data | scrambled data: middle; top 5%; most | p | verdict printed |
|---|---|---|---|---|---|
| stocks, one day -5% or worse | 2,118,940 | 115 | 12; 123; 417 | 0.066 | no more than luck |
| stocks, 5 sessions -10% or worse | 1,040,040 | 0 | 2; 21; 208 | 1.000 | no more than luck |
| funds, one day -3% or worse | 29,256 | 0 | 0; 3; 19 | 1.000 | no more than luck |
| funds, 5 sessions -7% or worse | 2,336 | 0 | 0; 0; 1 | 1.000 | no more than luck |
Inside the first group, the families with the most confirmed patterns: T1 + T2 (the fall and the market, with who fell and who set it off) 67 against a scrambled top-5% of 45; T1 alone 16 against 7; T1 + T4 18 against 29; T2 + T3 9 against 6; T2 + T8 2 against 0.
**Fault in the scrambling (Claude's), seen in the output itself.** In several families the REAL data produced far fewer 'found' patterns than scrambled data typically did (T4: 5 against 40; T1 + T4: 79 against 130; T2 + T4: 36 against 130). Scrambled data should look like real data when nothing is there, not richer. Cause: in the real data each day counts once (a crash day's sixty near-identical outcomes share one day's weight), but the scrambled copies slid the outcomes along the calendar and left the weights behind -- the same sixty outcomes landed on rows belonging to sixty quiet days and counted as sixty days. That made scrambled data look full of strong patterns and made the test too hard to pass. The fault works AGAINST finding patterns, so no false pattern was reported; but the verdict 'no more than luck' for the first group is not reliable either.
**Correction, registered before the re-run.** Each sell-off's outcome slides along the calendar TOGETHER WITH its weight, so each day still counts once in every scrambled copy; the support and the z of a pattern in a scrambled copy use that copy's weights. Nothing else changes: same groups, items, patterns, outcomes, thresholds (z 3.5; 60 and 30 day-equivalents; half the size), 300 repeats, bar p < 0.0125, candidate rule of 3.98. Check on made-up data: where nothing was planted, real and scrambled counts now agree (1 against a middle of 1); the planted pattern is still found. The real-data counts above (115, 0, 0, 0) do not depend on the scrambling; only the comparison changes -- and the FRED series are fetched again (with retries), which changes T4.
**Priors #193-#195:** scored after the corrected run.
"""
if "### 3.99 Sell-off stage D, first night run" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.99 added")
else: print("  TRACK.md: 3.99 already there -- skipped")
