"""record_26nov_tn1_result_and_debt_forward.py -- TRACK 3.142: the result of TN-1 (priors #249-#251 scored) and what it means for the pool plan; the forward record DN-F and the listener's 'new debt filed' note (founder's YES). Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.142 TN-1: result -- results sit at turns, most turns have no special news; the debt forward record and the listener's note (26 Nov 22:00)
**TN-1, result (commit 46f1e1a; `docs/turn_news.md`).** 20 pool stocks, 947 turns since June 2018; 133 Fed decision days, 1,217 TrendForce days; 409 slid copies; a cell passes under 0.0033 (the smallest chance the copies allow is 0.0024).
| kind of news | the session after the turn | the turn day or the session after | from the session before to two after |
|---|---|---|---|
| the company's own results | 4.2% of turns (ordinary 1.7%; 2.5 times) PASSES | 7.1% (3.3%; 2.1 times) PASSES | 12.7% (6.6%; 1.9 times) PASSES |
| its other 8-K filings | 3.9% (3.1%) no | 7.2% (6.1%) no | 13.8% (11.7%) no, chance 0.017 |
| any 8-K of the company | 8.1% (4.7%) no, chance 0.0049 | 14.1% (9.2%) PASSES | 24.9% (17.5%) PASSES |
| a Fed decision day | 4.3% (3.5%) no | 10.1% (6.9%) no, chance 0.02 | 18.2% (13.9%) no, chance 0.017 |
| a TrendForce release (chip companies) | 32.0% (29.7%) no | 58.4% (51.1%) no, chance 0.02 | 78.9% (76.8%) no |
**Any dated news near a turn** (own 8-K, Fed decision, TrendForce): the session after 24.2% of turns (ordinary days 19.7%); the turn day or the session after 41.9% (33.6%); the wider window 59.3% (51.7%).
**What it means for the founder's assumption (POOL_PLAN point 4).** Partly right. (1) A company's own results are found at turns about twice as often as on ordinary days -- established. (2) But they are there at only 7 turns in 100 (turn day or the session after): 93 in 100 turns have no results near them. (3) With every kind of dated news we hold counted together, a turn has such news near it only a little more often than an ordinary day does (42% against 34%). So **most turns are not explained by the dated news on file**; either they come from news we do not hold (press reports, other companies' news, analyst changes, the market as a whole) or from no news at all. The pool plan can keep 'results end trends' as a fact; 'every trend ends because of news' is not shown.
**Priors.** #249 (own results pass): RIGHT. #250 (fewer than 30% of turns have any dated news in 'turn day or the session after'): WRONG as written -- 41.9% -- but the point behind it holds: ordinary days have 33.6%. #251 (Fed days and TrendForce do not pass): RIGHT; both lean the same way (chance about 0.02) without passing.
**Founder, 26 Nov 17:18:** 'Yes for both. Summarize on what we have found so far ... in simple words ... one single paragraph.' The paragraph was given in the chat; its content is 3.119-3.142.
**(1) The forward record DN-F (`python -m src.debt_news forward`, in the daily block after `fetch`).** Every new CLEAN debt deal of Oracle, Meta, Alphabet, Amazon, Microsoft filed on or after 27 Nov 2026: the company's own share from the first open after the filing to that day's close and to the next day's close; beside it roughly what the 1x inverse fund (ORCS, METD, GGLS, AMZD, MSFD) would have made -- minus the share's move, minus 0.13 points for its measured spread. Verdict at 15 clean deals with a result (about two years at eight a year). Registered measure: the average to that day's close; the hint to beat is -0.70 points (DN-2), which did not repeat on other companies (DN-3).
**(2) The listener's note 'NEW DEBT FILED' (`src/market_wire.py`; needs a listener restart).** Once a minute the SEC's list of the newest filings is read for the debt forms (424B5, 424B2, 424B3, FWP) of 17 watched companies; a hit is printed in the listener's window and stored with the market-wide headlines (`data_provenance/live/market_wire.jsonl`). **Information only** under the founder's rule of 20 Nov: no test has passed on it, so it is not read by a paid model, not scored, not coloured, and not on the page as a signal.
"""
if "### 3.142 TN-1: result" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.142 added")
else: print("  TRACK.md: 3.142 already there -- skipped")
